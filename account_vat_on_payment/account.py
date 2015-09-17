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

from openerp.osv import orm
from tools.translate import _


class account_voucher(orm.Model):
    _inherit = "account.voucher"

    def is_vat_on_payment(self, voucher):
        vat_on_p = 0
        valid_lines = 0
        if voucher.type in ('payment', 'receipt'):
            for line in voucher.line_ids:
                if line.amount:
                    valid_lines += 1
                    if (
                        line.move_line_id and line.move_line_id.invoice
                        and line.move_line_id.invoice.vat_on_payment
                    ):
                        vat_on_p += 1
            if vat_on_p and vat_on_p != valid_lines:
                raise orm.except_orm(
                    _('Error'),
                    _("""Can't handle VAT on payment if not every invoice
                    is on a VAT on payment treatment"""))
        return vat_on_p

    def action_move_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        inv_pool = self.pool.get('account.invoice')
        #journal_pool = self.pool.get('account.journal')
        move_line_pool = self.pool.get('account.move.line')
        #move_pool = self.pool.get('account.move')
        currency_obj = self.pool.get('res.currency')
        res = False
        for voucher in self.browse(cr, uid, ids, context):
            res = super(account_voucher, self).action_move_line_create(
                cr, uid, [voucher.id], context)
            # because 'move_id' has been updated by 'action_move_line_create'
            voucher.refresh()
            if self.is_vat_on_payment(voucher):
                lines_to_create = []
                amounts_by_invoice = super(
                    account_voucher, self
                ).allocated_amounts_grouped_by_invoice(
                    cr, uid, voucher, context)
                for inv_id in amounts_by_invoice:
                    invoice = inv_pool.browse(cr, uid, inv_id, context)
                    company = self.pool['res.users'].browse(
                                cr, uid, uid).company_id
                    fiscal_position = invoice.fiscal_position and \
                        invoice.fiscal_position or \
                        company.default_property_account_position and \
                        company.default_property_account_position
                    if not fiscal_position:
                        raise orm.except_orm(_("Missing fiscal position!"),
                            _("Company %s has not a default fiscal position!")
                            % company.name)
                    for inv_move_line in invoice.move_id.line_id:
                        if (
                            inv_move_line.account_id.type != 'receivable'
                            and inv_move_line.account_id.type != 'payable'
                        ):
                            # compute the VAT or base line proportionally to
                            # the paid amount
                            if (voucher.exclude_write_off and
                                    voucher.payment_option == 'with_writeoff'):
                                # avoid including write-off if set in voucher.
                                # That means: use the invoice's total
                                # (as we are in 'full reconcile' case)
                                allocated_amount = amounts_by_invoice[
                                    invoice.id]['allocated']
                            else:
                                allocated_amount = (
                                    amounts_by_invoice[invoice.id]['allocated']
                                    +
                                    amounts_by_invoice[invoice.id]['write-off']
                                )
                            new_line_amount = currency_obj.round(
                                cr, uid, voucher.company_id.currency_id, (
                                    allocated_amount /
                                    amounts_by_invoice[invoice.id]['total']) *
                                (inv_move_line.credit or inv_move_line.debit)
                            )
                            new_line_amount_curr = False
                            if (amounts_by_invoice[invoice.id].get(
                                    'allocated_currency')
                                and amounts_by_invoice[invoice.id].get(
                                    'foreign_currency_id')):
                                for_curr = currency_obj.browse(
                                    cr, uid, amounts_by_invoice[
                                        invoice.id]['foreign_currency_id'],
                                    context=context)
                                if (voucher.exclude_write_off and
                                        voucher.payment_option == 'with_writeoff'):
                                    # again
                                    # avoid including write-off if set in
                                    # voucher.
                                    allocated_amount = amounts_by_invoice[
                                        invoice.id]['allocated_currency']
                                else:
                                    allocated_amount = (
                                        amounts_by_invoice[invoice.id][
                                            'allocated_currency'] +
                                        amounts_by_invoice[invoice.id][
                                            'currency-write-off']
                                    )
                                new_line_amount_curr = currency_obj.round(
                                    cr, uid, for_curr, (allocated_amount /
                                        amounts_by_invoice[invoice.id][
                                            'total_currency']) * (
                                                inv_move_line.amount_currency))

                            # prepare the opening move line for suspended vat
                            # mettere il periodo diverso per la fattura (però in
                            # questo caso bisogna creare un movimento separato
                            # P.S. non serve, i movimenti con vat_on_payment non
                            # devono essere considerati per i report (e magari per
                            # le viste)
                            vals = {
                                'name': inv_move_line.name,
                                'credit': (
                                    inv_move_line.credit and
                                    new_line_amount or 0.0),
                                'debit': (
                                    inv_move_line.debit and
                                    new_line_amount or 0.0),
                                'partner_id': (
                                    inv_move_line.partner_id
                                    and inv_move_line.partner_id.id or False),
                                'vat_on_payment': True,
                            }
                            #if inv_move_line.tax_vat_on_payment_id.is_base:
                            #    vals['account_id'] = invoice.fiscal_position.\
                            #    account_amount_vat_on_payment_id.id
                            #else:
                            if inv_move_line.tax_vat_on_payment_id.is_base:
                                vals['account_id'] = fiscal_position.\
                                account_amount_vat_on_payment_id.id
                            else:
                                vals['account_id'] = inv_move_line.account_vat_on_payment_id.id
                            if new_line_amount_curr:
                                vals['amount_currency'] = new_line_amount_curr
                                vals['currency_id'] = for_curr.id

                            if inv_move_line.tax_vat_on_payment_id:
                                vals['tax_code_id'] = inv_move_line.tax_vat_on_payment_id.id
                                if inv_move_line.tax_amount < 0:
                                    vals['tax_amount'] = -new_line_amount
                                else:
                                    vals['tax_amount'] = new_line_amount

                            lines_to_create.append(vals)

                            # create the reversal move closing vat
                            vals_rev = {
                                'name': inv_move_line.name,
                                'credit': (
                                    inv_move_line.debit and
                                    new_line_amount or 0.0),
                                'debit': (
                                    inv_move_line.credit and
                                    new_line_amount or 0.0),
                                'partner_id': (
                                    inv_move_line.partner_id
                                    and inv_move_line.partner_id.id or False),
                                'vat_on_payment': True,
                            }
                            if inv_move_line.tax_vat_on_payment_id.is_base:
                                vals_rev['account_id'] = fiscal_position.\
                                account_amount_vat_on_payment_id.id
                            else:
                                vals_rev['account_id'] = fiscal_position.\
                                account_tax_vat_on_payment_id.id
                            if new_line_amount_curr:
                                vals_rev['amount_currency'] = new_line_amount_curr
                                vals_rev['currency_id'] = for_curr.id

                            if inv_move_line.tax_vat_on_payment_id:
                                vals_rev['tax_vat_on_payment_id'
                                ] = inv_move_line.tax_vat_on_payment_id.id
                                if inv_move_line.tax_amount < 0:
                                    vals_rev['tax_amount'] = new_line_amount
                                else:
                                    vals_rev['tax_amount'] = -new_line_amount

                            lines_to_create.append(vals_rev)

                for line_to_create in lines_to_create:
                    line_to_create['move_id'] = voucher.move_id.id

                    move_line_pool.create(cr, uid, line_to_create, context)

                voucher.move_id.write({'journal_vat_on_payment_id':invoice.journal_id.id})

                #voucher.write({'shadow_move_id': shadow_move_id})

                #super(account_voucher, self).balance_move(
                #    cr, uid, shadow_move_id, context)
                #super(account_voucher, self).balance_move(
                #    cr, uid, voucher.move_id.id, context)

        return res

#    def cancel_voucher(self, cr, uid, ids, context=None):
#        res = super(account_voucher, self).cancel_voucher(
#            cr, uid, ids, context)
#        reconcile_pool = self.pool.get('account.move.reconcile')
#        move_pool = self.pool.get('account.move')
#        for voucher in self.browse(cr, uid, ids, context=context):
#            recs = []
#            if voucher.shadow_move_id:
#                for line in voucher.shadow_move_id.line_id:
#                    if line.reconcile_id:
#                        recs += [line.reconcile_id.id]
#                    if line.reconcile_partial_id:
#                        recs += [line.reconcile_partial_id.id]
#
#                reconcile_pool.unlink(cr, uid, recs)
#
#                if voucher.shadow_move_id:
#                    move_pool.button_cancel(
#                        cr, uid, [voucher.shadow_move_id.id])
#                    move_pool.unlink(cr, uid, [voucher.shadow_move_id.id])
#        return res
