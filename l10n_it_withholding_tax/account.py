# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>)    
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tools.translate import _


class res_company(orm.Model):
    _inherit = 'res.company'
    _columns = {
        'withholding_journal_id': fields.many2one('account.journal', 'Withholding journal', help="Journal used for registration of witholding amounts to be paid"),
        }


class account_tax(orm.Model):
    _inherit = 'account.tax.code'
    _columns = {
        'withholding_type': fields.boolean("Ritenuta d'acconto"),
        'withholding_payment_term_id': fields.many2one('account.payment.term', "Termine di pagamento ritenuta d'acconto"),
    }


class account_voucher(orm.Model):
    _inherit = "account.voucher"
    
    _columns = {
        'withholding_move_ids': fields.many2many('account.move', 'voucher_withholding_move_rel', 'voucher_id', 'move_id', 'Withholding Tax Entries', readonly=True),
        }

    def reconcile_withholding_move(self, cr, uid, invoice, wh_move, context=None):
        line_pool = self.pool['account.move.line']
        rec_ids = []
        for inv_move_line in invoice.move_id.line_id:
            if inv_move_line.account_id.type == 'payable' and not inv_move_line.reconcile_id and inv_move_line.tax_code_id.withholding_type:
                rec_ids.append(inv_move_line.id)
        for wh_line in wh_move.line_id:
            if wh_line.account_id.type == 'payable' and not wh_line.reconcile_id and wh_line.debit:
                rec_ids.append(wh_line.id)
        return line_pool.reconcile_partial(cr, uid, rec_ids, type='auto', context=context)

    def action_move_line_create(self, cr, uid, ids, context=None):
        res = super(account_voucher, self).action_move_line_create(cr, uid, ids, context)
        move_pool = self.pool['account.move']
        curr_pool = self.pool['res.currency']
        term_pool = self.pool['account.payment.term']
        for voucher in self.browse(cr, uid, ids, context):
            for line in voucher.line_ids:
                if line.amount and line.move_line_id and line.move_line_id.invoice and not line.move_line_id.tax_code_id.id:
                    invoice = line.move_line_id.invoice
                    for inv_tax_line in line.move_line_id.invoice.invoice_line:
                        for tax_line in inv_tax_line.invoice_line_tax_id:
                            if tax_line.tax_code_id.withholding_type:
                                if voucher.type != 'payment':
                                    raise orm.except_orm(_('Error'), _('Can\'t handle withholding tax with voucher of type other than payment'))
                                if not tax_line.tax_code_id.withholding_payment_term_id:
                                    raise orm.except_orm(_('Error'), _('The tax does not have an associated Withholding Payment Term'))
                                if not invoice.company_id.withholding_journal_id:
                                    raise orm.except_orm(_('Error'), _('The company does not have an associated Withholding journal'))
                                due_list = term_pool.compute(
                                    cr, uid, tax_line.tax_code_id.withholding_payment_term_id.id, line.amount,
                                    date_ref=voucher.date or invoice.date_invoice, context=context)
                                if len(due_list) > 1:
                                    raise orm.except_orm(
                                        _('Error'),
                                        _('The payment term %s has too many due dates')
                                        % tax_line.tax_code_id.withholding_payment_term_id.name)
                                if len(due_list) == 0:
                                    raise orm.except_orm(
                                        _('Error'),
                                        _('The payment term %s does not have due dates')
                                        % tax_line.tax_code_id.withholding_payment_term_id.name)
                                # compute the amount of withholding tax to pay, proportionally to paid amount
                                new_line_amount = curr_pool.round(cr, uid, voucher.company_id.currency_id, (
                                 line.amount/invoice.amount_total * inv_tax_line.price_subtotal * - tax_line.amount)
                                 )
                                new_move = {
                                    'journal_id': invoice.company_id.withholding_journal_id.id,
                                    'line_id': [
                                        (0, 0, {
                                            'name': _('Giro contabile ritenuta acconto - ') + invoice.number,
                                            'account_id': tax_line.account_collected_id.id,
                                            'debit': new_line_amount,
                                            'credit': 0.0,
                                            }),
                                        (0, 0, {
                                            'name': _('Giro contabile ritenuta acconto - ') + invoice.number,
                                            'account_id': tax_line.account_collected_id.id,
                                            'debit': 0.0,
                                            'credit': new_line_amount,
                                            'date_maturity': due_list[0][0],
                                            'partner_id': invoice.partner_id.id,
                                            }),
                                        ]
                                    }
                                move_id = self.pool['account.move'].create(cr, uid, new_move, context=context)
                                self.reconcile_withholding_move(
                                    cr, uid, invoice, move_pool.browse(cr, uid, move_id, context), context)
                                voucher.write({'withholding_move_ids': [(4, move_id)]})
        return res

    def cancel_voucher(self, cr, uid, ids, context=None):
        res = super(account_voucher, self).cancel_voucher(cr, uid, ids, context)
        move_pool = self.pool['account.move']
        for voucher in self.browse(cr, uid, ids, context=context):
            for move in voucher.withholding_move_ids:
                move_pool.button_cancel(cr, uid, [move.id])
                move_pool.unlink(cr, uid, [move.id])
        return res
