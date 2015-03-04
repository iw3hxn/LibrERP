# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import datetime


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def _is_direct_invoice(self, cr, uid, ids, filed_name, args, context=None):
        """
        u'IN/00429-OUT/00366-return:CNL/2015/000374, IN/00367-OUT/00217-return:CNL/2015/000350'
        u'OUT/00441:1224/15 Consuntivo'
        u'IN/00266:PO00350:SO154'

        """
        result = {}
        if ids:
            invoices = self.browse(cr, uid, ids, context)
            for invoice in invoices:
                result[invoice.id] = False
                # if hasattr(invoice, 'move_products') and invoice.move_products:
                #     result[invoice.id] = True
                if invoice.origin:
                    for origin in invoice.origin.split(','):
                        if ':' in origin:
                            picking_name = origin.split(':')[0] # picking is first element
                        else:
                            picking_name = origin
                        picking_out_ids = self.pool['stock.picking'].search(cr, uid, [('type', '=', 'out'), ('name', '=', picking_name)], context=context)
                        if picking_out_ids:
                            picking = self.pool['stock.picking'].browse(cr, uid, picking_out_ids[0], context=context)
                            if not picking.ddt_number:
                                result[invoice.id] = True
                                break
        return result

    def action_number(self, cr, uid, ids, context=None):
        super(account_invoice, self).action_number(cr, uid, ids, context)
        for obj_inv in self.browse(cr, uid, ids):
            inv_type = obj_inv.type
            number = obj_inv.number
            date_invoice = obj_inv.date_invoice
            reg_date = obj_inv.registration_date
            journal = obj_inv.journal_id.id
            fy = obj_inv.period_id.fiscalyear_id
            fy_id = obj_inv.period_id.fiscalyear_id.id

            period = obj_inv.period_id
            vat_statement = self.pool['account.vat.period.end.statement'].search(cr, uid, [('period_ids', 'in', period.id)])
            if vat_statement and self.pool['account.vat.period.end.statement'].browse(cr, uid, vat_statement)[0].state != 'draft':
                raise orm.except_orm(
                    _('Period Mismatch Error!'),
                    _('Period %s have already a closed vat statement.')
                    % (period.name)
                )

            #check correct typing of number - for module account_invoice_force_number (#TODO move code in that module?)
            for as_fy in obj_inv.journal_id.sequence_id.fiscal_ids:
                prefix = as_fy.sequence_id.prefix

                # check if it isn't an old db with %(fy) in sequence - #TODO show a message to correct the sequences
                if prefix and prefix.find('fy') == -1:  # continue check only if not found
                    if as_fy.fiscalyear_id == fy:
                        padding = as_fy.sequence_id.padding
                        if len(number) != padding + len(prefix):
                            raise orm.except_orm(
                                _('Number Mismatch Error!'),
                                _('Length not correct: prefix %s with number of %s length')
                                % (prefix, padding)
                            )

                        if number[:-padding] != prefix:
                            raise orm.except_orm(
                                _('Number Mismatch Error !'),
                                _('Prefix not correct: %s')
                                % (prefix)
                            )

                        if not number[-padding:].isdigit():
                            raise orm.except_orm(
                                _('Number Mismatch Error!'),
                                _('After prefix only digits are permitted')
                            )

            period_ids = self.pool['account.period'].search(
                cr, uid, [('fiscalyear_id', '=', fy_id), ('company_id', '=', obj_inv.company_id.id)])
            if inv_type == 'out_invoice' or inv_type == 'out_refund':
                res = self.search(cr, uid, [('type', '=', inv_type), ('date_invoice', '>', date_invoice),
                                            ('number', '<', number), ('journal_id', '=', journal),
                                            ('period_id', 'in', period_ids)])
                if res:
                    raise orm.except_orm(_('Date Inconsistency'),
                                         _('Cannot create invoice! Post the invoice with a greater date'))
            if inv_type == 'in_invoice' or inv_type == 'in_refund':
                res = self.search(cr, uid, [('type', '=', inv_type), ('registration_date', '>', reg_date),
                                            ('number', '<', number), ('journal_id', '=', journal),
                                            ('period_id', 'in', period_ids)], context=context)
                if res:
                    raise orm.except_orm(_('Date Inconsistency'),
                                         _('Cannot create invoice! Post the invoice with a greater date'))
                supplier_invoice_number = obj_inv.supplier_invoice_number
                partner_id = obj_inv.partner_id.id
                res = self.search(cr, uid, [('type', '=', inv_type), ('date_invoice', '=', date_invoice),
                                            ('journal_id', '=', journal),
                                            ('supplier_invoice_number', '=', supplier_invoice_number),
                                            ('partner_id', '=', partner_id),
                                            ('state', 'not in', ('draft', 'cancel'))], context=context)
                if res:
                    raise orm.except_orm(_('Invoice Duplication'),
                                         _('Invoice already posted!'))
        return True

    def onchange_partner_id(self, cr, uid, ids, i_type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False, context=None):
        result = super(account_invoice, self).onchange_partner_id(
            cr, uid, ids, i_type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        fp_result = self.onchange_check_fiscal_position(cr, uid, ids, date_invoice, partner_id)
        if fp_result['value']:
            result['value']['fiscal_position'] = fp_result['value']['fiscal_position']
        #set company payment if missing payment_term
        company_id = self.pool['res.users'].browse(cr, uid, uid, context).company_id.id
        company_obj = self.pool['res.company']
        company = company_obj.browse(cr, uid, company_id, context)
        partner = self.pool['res.partner'].browse(cr, uid, partner_id, context)
        if not partner.property_payment_term:
            payment_term_company = company.default_property_payment_term.id
            result['value']['payment_term'] = payment_term_company
        return result

    def onchange_check_fiscal_position(self, cr, uid, ids, date_invoice, partner_id, context=None):
        if partner_id:
            if not date_invoice:
                date_invoice = datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
            fiscal_position_ids = self.pool['account.fiscal.position'].search(cr, uid, [
                ('partner_id', '=', partner_id), ('end_validity', '>=', date_invoice), '|', ('date', '<=', date_invoice), ('date', '=', False)
            ])
            if fiscal_position_ids:
                return {'value': {'fiscal_position': fiscal_position_ids[0]}}
            else:
                partner = self.pool['res.partner'].browse(cr, uid, partner_id, context)
                if partner.property_account_position:
                    return {'value': {'fiscal_position': partner.property_account_position.id}}
                else:
                    return {'value': {'fiscal_position': False}}
        return {'value': {}}

    _columns = {
        'supplier_invoice_number': fields.char('Supplier invoice nr', size=16),
        'direct_invoice': fields.function(_is_direct_invoice, string='Direct Invoice', type='boolean', method=True),
        'cig': fields.char('CIG', size=64, help="Codice identificativo di gara"),
        'cup': fields.char('CUP', size=64, help="Codice unico di Progetto")
#        'reference': fields.related('supplier_invoice_number', type='char' ),
    }
