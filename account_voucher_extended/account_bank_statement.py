# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


from openerp.osv import fields, orm
from openerp.tools.translate import _


class account_bank_statement_line(orm.Model):
    _inherit = "account.bank.statement.line"
    # _columns = {
    #     'journal_id': fields.related("statement_id", "journal_id", type="many2one", relation='account.journal', string="Journal"),
    # }


    def add_reconciliation(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''

        mod_obj = self.pool['ir.model.data']
        act_obj = self.pool['ir.actions.act_window']

        fields = {
             'amount', 'period_id', 'partner_id', 'journal_id', 'currency_id', 'reference', 'narration', 'type', 'pay_now', 'name', 'date', 'company_id', 'tax_id', 'payment_option', 'comment', 'payment_rate', 'payment_rate_currency_id',
        }

        for line in self.browse(cr, uid, ids, context=context):
            if line.statement_id.state != 'draft':
                raise orm.except_orm(_('Error!'),
                _("The Bank Statement Must be on draft."))
            if line.type == 'customer':
                res = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_form')
            elif line.type == 'supplier':
                res = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_vendor_payment_form')
            else:
                return False

            if line.amount > 0:
                ttype = 'receipt'
            else:
                ttype = 'payment'

            context.update({'amount': abs(line.amount), 'line_type': line.type, 'default_type': ttype, 'type': ttype, 'default_partner_id': line.partner_id.id, 'default_journal_id': line.statement_id.journal_id.id, 'default_amount': abs(line.amount), 'default_reference': line.ref, 'default_date': line.date, 'default_name': line.name})
            vals = self.pool['account.voucher'].default_get(cr, uid, fields, context)
            account_id = line.statement_id.journal_id.default_credit_account_id or line.statement_id.journal_id.default_debit_account_id
            vals.update({'account_id': account_id.id})
            context.update({'account_bank_statement_line_id': line.id})
            # vals.update(self.pool['account.voucher'].onchange_partner_id(cr, uid, line.partner_id.id, line.journal_id.id, line.amount, line.statement_id.currency and line.statement_id.currency.id, line.type, line.date, result['context']))
            voucher_id = self.pool['account.voucher'].create(cr, uid, vals, context=context)
            value = self.pool['account.voucher'].recompute_voucher_lines(cr, uid, [voucher_id], line.partner_id.id, line.statement_id.journal_id.id, abs(line.amount), line.statement_id.currency and line.statement_id.currency.id, ttype, line.date, context=context).get('value')
            if ttype == 'receipt':
                for vals_line in value.get('line_cr_ids'):
                    vals_line.update({'voucher_id': voucher_id})
                    self.pool['account.voucher.line'].create(cr, uid, vals_line, context=context)
            if ttype == 'payment':
                for vals_line in value.get('line_dr_ids'):
                    vals_line.update({'voucher_id': voucher_id})
                    self.pool['account.voucher.line'].create(cr, uid, vals_line, context=context)
            line.write({'voucher_id': voucher_id})

            result = {
                'type': 'ir.actions.act_window',
                'name': 'Reconciliation',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': res and res[1] or False,
                'res_model': 'account.voucher',
                'nodestroy': True,
                'target': 'new',
                'res_id': voucher_id,
                'context': context,
            }

            return result

