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

    def get_total_tax_fiscal(self, cr, uid, ids, context=None):
        invoice = self.browse(cr, uid, ids[0], context)
        amount_withholding = 0.0
        for line in invoice.tax_line:
            if line.tax_code_id.notprintable:
                amount_withholding += line.tax_amount
        if amount_withholding != 0.0:
            return invoice.amount_tax - amount_withholding
        return invoice.amount_tax

    def get_total_fiscal(self, cr, uid, ids, context=None):
        invoice = self.browse(cr, uid, ids[0], context)
        amount_withholding = 0.0
        for line in invoice.tax_line:
            if line.tax_code_id.notprintable:
                amount_withholding += line.tax_amount
        if amount_withholding != 0.0:
            return invoice.amount_total - amount_withholding
        return invoice.amount_total

    def action_cancel(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids, context):
            period = invoice.period_id
            vat_statement = self.pool['account.vat.period.end.statement'].search(
                cr, uid, [('period_ids', 'in', period.id)], context=context)
            if vat_statement and self.pool['account.vat.period.end.statement'].browse(
                    cr, uid, vat_statement, context)[0].state != 'draft':
                raise orm.except_orm(
                    _('Period Mismatch Error!'),
                    _('Period %s have already a closed vat statement.')
                    % period.name
                )
        return super(account_invoice, self).action_cancel(cr, uid, ids, context)

    def _is_direct_invoice(self, cr, uid, ids, filed_name, args, context=None):
        """
        u'IN/00429-OUT/00366-return:CNL/2015/000374, IN/00367-OUT/00217-return:CNL/2015/000350'
        u'OUT/00441:1224/15 Consuntivo'
        u'IN/00266:PO00350:SO154'

        """
        result = {}

        for invoice in self.browse(cr, uid, ids, context):
            result[invoice.id] = False
            # if hasattr(invoice, 'move_products') and invoice.move_products:
            # result[invoice.id] = True
            if invoice.origin:
                for origin in invoice.origin.split(','):
                    if ':' in origin:
                        picking_name = origin.split(':')[0]  # picking is first element
                    else:
                        picking_name = origin
                    picking_out_ids = self.pool['stock.picking'].search(cr, uid, [('type', '=', 'out'),
                                                                                  ('name', '=', picking_name)],
                                                                        context=context)
                    if picking_out_ids:
                        picking = self.pool['stock.picking'].browse(cr, uid, picking_out_ids[0], context=context)
                        if not picking.ddt_number:
                            result[invoice.id] = True
                            break
        return result

    def action_number(self, cr, uid, ids, context=None):
        if not context:
            context = {}

        result = super(account_invoice, self).action_number(cr, uid, ids, context)

        for invoice in self.browse(cr, uid, ids, context):
            inv_type = invoice.type
            internal_number = invoice.internal_number
            number = invoice.number
            date_invoice = invoice.date_invoice
            reg_date = invoice.registration_date
            journal_id = invoice.journal_id.id
            # fy = obj_inv.period_id.fiscalyear_id
            fy_id = invoice.period_id.fiscalyear_id.id
            period = invoice.period_id
            vat_statement = self.pool['account.vat.period.end.statement'].search(cr, uid, [('period_ids', 'in', period.id)], context=context)
            if vat_statement and self.pool['account.vat.period.end.statement'].browse(cr, uid, vat_statement, context)[0].state != 'draft':
                raise orm.except_orm(
                    _('Period Mismatch Error!'),
                    _('Period %s have already a closed vat statement.')
                    % period.name
                )

            # COMMENT WRONG CODE
            # #check correct typing of number - for module account_invoice_force_number (#TODO move code in that module?)
            # for as_fy in obj_inv.journal_id.sequence_id.fiscal_ids:
            #     prefix = as_fy.sequence_id.prefix
            #
            #     # check if it isn't an old db with %(fy) in sequence - #TODO show a message to correct the sequences
            #     if prefix and prefix.find('fy') == -1:  # continue check only if not found
            #         if as_fy.fiscalyear_id == fy:
            #             padding = as_fy.sequence_id.padding
            #             if len(number) != padding + len(prefix):
            #                 raise orm.except_orm(
            #                     _('Number Mismatch Error!'),
            #                     _('Length not correct: prefix %s with number of %s length')
            #                     % (prefix, padding)
            #                 )
            #
            #             if number[:-padding] != prefix:
            #                 raise orm.except_orm(
            #                     _('Number Mismatch Error !'),
            #                     _('Prefix not correct: %s')
            #                     % (prefix)
            #                 )
            #
            #             if not number[-padding:].isdigit():
            #                 raise orm.except_orm(
            #                     _('Number Mismatch Error!'),
            #                     _('After prefix only digits are permitted')
            #                 )

            period_ids = self.pool['account.period'].search(
                cr, uid, [('fiscalyear_id', '=', fy_id), ('company_id', '=', invoice.company_id.id)], context=context)
            
            if inv_type in ['out_invoice', 'out_refund']:
                res = self.search(cr, uid, [('type', '=', inv_type), ('date_invoice', '>', date_invoice),
                                            ('number', '<', number), ('journal_id', '=', journal_id),
                                            ('period_id', 'in', period_ids)], context=context)
                if res and not internal_number:
                    raise orm.except_orm(_('Date Inconsistency'),
                                         _('Cannot create invoice! Post the invoice with a greater date'))
            if inv_type in ['in_invoice', 'in_refund']:
                res = self.search(cr, uid, [('type', '=', inv_type), ('registration_date', '>', reg_date),
                                            ('number', '<', number), ('journal_id', '=', journal_id),
                                            ('period_id', 'in', period_ids)], context=context)
                if res and not internal_number:
                    raise orm.except_orm(_('Date Inconsistency'),
                                         _('Cannot create invoice! Post the invoice with a greater date'))
                supplier_invoice_number = invoice.supplier_invoice_number
                partner_id = invoice.partner_id.id
                res = self.search(cr, uid, [('type', '=', inv_type), ('date_invoice', '=', date_invoice),
                                            ('journal_id', '=', journal_id),
                                            ('supplier_invoice_number', '=', supplier_invoice_number),
                                            ('partner_id', '=', partner_id),
                                            ('state', 'not in', ('draft', 'cancel'))], context=context)
                if res:
                    raise orm.except_orm(_('Invoice Duplication'),
                                         _('Invoice already posted!'))
        return result

    def onchange_partner_id(self, cr, uid, ids, i_type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False, context=None):
        result = super(account_invoice, self).onchange_partner_id(
            cr, uid, ids, i_type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        fp_result = self.onchange_check_fiscal_position(cr, uid, ids, date_invoice, partner_id)
        if fp_result['value']:
            result['value']['fiscal_position'] = fp_result['value']['fiscal_position']
        # set company payment if missing payment_term
        company_id = self.pool['res.users'].browse(cr, uid, uid, context).company_id.id
        company = self.pool['res.company'].browse(cr, uid, company_id, context)
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
                return {
                    'value': {
                        'fiscal_position': partner.property_account_position and partner.property_account_position.id or False
                    }
                }

        return {'value': {}}

    def invoice_validate_check(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.type in ['out_invoice', 'out_refund']:
                if invoice.company_id.stop_invoice_internal_number:
                    invoice_ids = self.search(cr, 1, [('internal_number', '!=', True), ('type', '=', 'out_invoice'),
                                                      ('journal_id', '=', invoice.journal_id.id), ('state', '=', 'draft')],
                                              context=context)
                    for invoice_old in self.browse(cr, 1, [x for x in invoice_ids if x not in ids], context):
                        raise orm.except_orm(_('Invoice'),
                                             _(
                                                 'Impossible to Validate, there are just an invoice of {partner} that was just validate with number {invoice_number}').format(
                                                 partner=invoice_old.partner_id.name,
                                                 invoice_number=invoice_old.internal_number))

                if not invoice.payment_term and invoice.company_id.check_invoice_payment_term:
                    raise orm.except_orm(_('Invoice'),
                                         _(
                                             'Impossible to Validate, need to set Payment Term on invoice of {partner}').format(
                                             partner=invoice.partner_id.name))

                if not invoice.fiscal_position and invoice.company_id.check_invoice_fiscal_position:
                    raise orm.except_orm(_('Invoice'),
                                         _(
                                             'Impossible to Validate, need to set Fiscal Position on invoice of {partner}').format(
                                             partner=invoice.partner_id.name))

                elif invoice.fiscal_position.required_tax:
                    if invoice.type in ['out_invoice', 'out_refund']:
                        invoice.button_reset_taxes()
                        if not invoice.tax_line:
                            raise orm.except_orm(_('Invoice'),
                                                 _(
                                                     'Impossible to Validate, need to set on Tax Line on invoice of {partner}').format(
                                                     partner=invoice.partner_id.name))

                if invoice.fiscal_position and not invoice.fiscal_position.no_check_vat:
                    vat_on_parent = False
                    vat_on_partner = False

                    if invoice.partner_id.parent_id:
                        if invoice.partner_id.parent_id.vat or invoice.partner_id.parent_id.cf:
                            vat_on_parent = True

                    elif invoice.partner_id.vat or invoice.partner_id.cf:
                        vat_on_partner = True

                    if not (vat_on_parent or vat_on_partner):
                        raise orm.except_orm(_('Invoice'),
                                             _('Impossible to Validate, need to set on Partner {partner} VAT').format(
                                                 partner=invoice.partner_id.name))
                        return False

            elif not invoice.supplier_invoice_number:
                raise orm.except_orm(_('Supplier Invoice'),
                                     _('Impossible to Validate, need to set Supplier invoice nr'))
                return False

            # check if internal number is on recovery sequence
            if invoice.internal_number:
                recovery_ids = self.pool['ir.sequence_recovery'].search(cr, uid, [('name', '=', 'account.invoice'), ('sequence', '=', invoice.internal_number)], context=context)
                if recovery_ids:
                    recovery_id = recovery_ids[0]
                    self.pool['ir.sequence_recovery'].write(cr, uid, recovery_id, {'active': False}, context)
        return True

    def invoice_cancel_check(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.internal_number:
                raise orm.except_orm(_('Invoice'),
                                     _('Impossible to Cancel, need to cancel Internal Number {number}').format(
                                         number=invoice.internal_number))

                return False

        return True

    def invoice_proforma_check(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.internal_number:
                raise orm.except_orm(_('Invoice'),
                                     _('Impossible to Proforma, need to cancel Internal Number {number}').format(
                                         number=invoice.internal_number))
                return False

        return True

    _columns = {
        'supplier_invoice_number': fields.char('Supplier invoice nr', size=16),
        'direct_invoice': fields.function(_is_direct_invoice, string='Direct Invoice', type='boolean', method=True),
        'cig': fields.char('CIG', size=64, help="Codice identificativo di gara"),
        'cup': fields.char('CUP', size=64, help="Codice unico di Progetto")
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        if not default:
            default = {}

        # We want supplier_invoice_number, cig, cup to be recreated:
        default.update({
            'supplier_invoice_number': False,
            'internal_number': False,
            'cig': False,
            'cup': False,
        })
        return super(account_invoice, self).copy(cr, uid, ids, default, context)

    def write(self, cr, uid, ids, vals, context=None):

        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        if isinstance(ids, (int, long)):
            ids = [ids]

        if 'internal_number' in vals.keys():
            if not vals['internal_number'] or vals['internal_number'].replace(' ', '') == '':
                if not self.pool['res.groups'].user_in_group(cr, uid, uid, 'account.group_number_account_invoice', context):
                    raise orm.except_orm(_("You don't have Permission!"), _("You must be on group 'Cancel Internal Number'"))
                for invoice in self.browse(cr, uid, ids, context):
                    self.pool['ir.sequence_recovery'].set(cr, uid, [invoice.id], 'account.invoice', 'internal_number', '', invoice.journal_id.sequence_id.id)

        return super(account_invoice, self).write(cr, uid, ids, vals, context)
