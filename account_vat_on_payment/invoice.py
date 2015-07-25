# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2012 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from tools.translate import _


class account_invoice(orm.Model):
    _inherit = "account.invoice"
    
    def _get_vat_on_payment(self, cr, uid, context=None):
        return self.pool.get('res.users').browse(
            cr, uid, uid, context).company_id.vat_on_payment

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """
        
        """
        move_lines = super(account_invoice, self).finalize_invoice_move_lines(
            cr, uid, invoice_browse, move_lines)
        #acc_pool = self.pool.get('account.account')
        tax_code_pool = self.pool.get('account.tax.code')
        new_move_lines = []
        for line_tup in move_lines:
            if invoice_browse.vat_on_payment:
                if line_tup[2].get('tax_code_id', False):
                    tax_code = tax_code_pool.browse(
                        cr, uid, line_tup[2]['tax_code_id'])
                    line_tup[2]['vat_on_payment'] = True
                    # we save the tax_code_id for future reversal move
                    line_tup[2]['tax_vat_on_payment_id'] = (
                        line_tup[2]['tax_code_id'])
                    line_tup[2]['tax_code_id'] = []
                    line_tup[2]['account_vat_on_payment_id'] = (
                        line_tup[2]['account_id'])
                    if not tax_code.is_base:
                        if not invoice_browse.fiscal_position:
                            company = self.pool['res.users'].browse(
                                cr, uid, uid).company_id
                            if not company.default_property_account_position:
                                raise orm.except_orm(_("Missing fiscal position!"),
                                    _("Company %s has not a default fiscal position!")
                                    % company.name)
                            else:
                                line_tup[2]['account_id'] = (
                                    company.default_property_account_position.account_tax_vat_on_payment_id.id)
                        else:
                            if invoice_browse.fiscal_position.account_tax_vat_on_payment_id:
                                line_tup[2]['account_id'] = (
                                    invoice_browse.fiscal_position.account_tax_vat_on_payment_id.id)
                            else:
                                raise orm.except_orm(_("Missing VAT on Payment account for reversal moves"),
                                    _("for '{}' fiscal position!").format(invoice_browse.fiscal_position.name))

            new_move_lines.append(line_tup)
        return new_move_lines

    def onchange_partner_id(
            self, cr, uid, ids, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice, self).onchange_partner_id(
            cr, uid, ids, type, partner_id, date_invoice, payment_term,
            partner_bank_id, company_id)
        # default value for VAT on Payment is changed every time the
        # customer/supplier is changed
        partner_obj = self.pool.get("res.partner")
        if partner_id:
            p = partner_obj.browse(cr, uid, partner_id)
            res['value']['vat_on_payment'] = p.property_account_position\
                and p.property_account_position.default_has_vat_on_payment\
                or False
        return res

    _columns = {
        'vat_on_payment': fields.boolean('Vat on payment'),
    }
    _defaults = {
        'vat_on_payment': _get_vat_on_payment,
    }
