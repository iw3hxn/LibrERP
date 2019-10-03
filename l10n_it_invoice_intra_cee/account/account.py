# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

import logging

import decimal_precision as dp
from openerp import netsvc
from openerp.osv import fields, orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class account_fiscal_position(orm.Model):

    _inherit = 'account.fiscal.position'

    _columns = {
        'account_transient_id': fields.many2one(
            'account.account', 'Account CEE'),
        'journal_auto_invoice_id': fields.many2one(
            'account.journal', 'Journal Auto Invoice CEE'),
        'journal_transfer_entry_id': fields.many2one(
            'account.journal',
            'Transfer Entry Journal'),
        'active_reverse_charge': fields.boolean('Active Reverse Charge Management'),
        'active_extra_ue_service': fields.boolean('Active Extra UE Service Management'),
        'extra_ue_line_detail': fields.text(
            'Extra UE Line Detail',
            help='Text used as description line in Extra UE Auto Invoice'),
        'extra_ue_service_tax_id': fields.many2one(
            'account.tax',
            'Extra UE Service Tax'),
        'auto_invoice_partner_id': fields.many2one(
            'res.partner', 'Auto Invoice Partner',
            help="Partner used for auto invoice, if use_same_partner is not set as True"),
        'use_same_partner': fields.boolean('Use the same partner of purchase invoice \
            for auto invoice'),
    }

    def _check_active_type_value(self, cr, uid, ids, context=None):
        for afp in self.browse(cr, uid, ids, context):
            flag = 0
            if afp.active_reverse_charge:
                flag += 1
            if afp.active_extra_ue_service:
                flag += 1
            if flag > 1:
                return False
        return True

    _constraints = [
        (_check_active_type_value,
            'Error!\nYou cannot create select two or more flag for time',
            ['active_reverse_charge', 'active_extra_ue_service']),
    ]


class account_tax(orm.Model):

    _inherit = 'account.tax'

    _columns = {
        'auto_invoice_tax_id': fields.many2one('account.tax',
                                               'Auto Invoice Tax'),
    }


class account_invoice(orm.Model):

    _inherit = 'account.invoice'

    def _auto_invoice_amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        tax_obj = self.pool['account.tax']
        for invoice in self.browse(cr, uid, ids, context=context):
            fp = invoice.fiscal_position
            res[invoice.id] = {
                'auto_invoice_amount_untaxed': 0.0,
                'auto_invoice_amount_tax': 0.0,
                'auto_invoice_amount_total': 0.0
            }
            if invoice.auto_invoice_id:
                res[invoice.id] = {
                    'auto_invoice_amount_untaxed': invoice.auto_invoice_id.amount_untaxed,
                    'auto_invoice_amount_tax': invoice.auto_invoice_id.amount_tax,
                    'auto_invoice_amount_total': invoice.auto_invoice_id.amount_total
                }
            else:
                for line in invoice.invoice_line:
                    line_reverse_charge = False
                    for tax in line.invoice_line_tax_id:
                        line_reverse_charge = True if tax.auto_invoice_tax_id else False
                    if fp and fp.active_reverse_charge and line_reverse_charge:
                        res[invoice.id][
                            'auto_invoice_amount_untaxed'] += line.price_subtotal
                        for t in tax_obj.compute_all(
                                cr, uid, line.invoice_line_tax_id,
                                (line.price_unit * (1-(
                                    line.discount or 0.0)/100.0)),
                                line.quantity, line.product_id)['taxes']:
                            res[invoice.id][
                                'auto_invoice_amount_tax'] += t['amount']
                    if (not fp) or (fp and not fp.active_reverse_charge):
                        res[invoice.id][
                            'auto_invoice_amount_untaxed'] += line.price_subtotal
                        for t in tax_obj.compute_all(
                                cr, uid, line.invoice_line_tax_id,
                                (line.price_unit * (1-(
                                    line.discount or 0.0)/100.0)),
                                line.quantity, line.product_id)['taxes']:
                            res[invoice.id][
                                'auto_invoice_amount_tax'] += t['amount']
                res[invoice.id]['auto_invoice_amount_total'] = res[
                    invoice.id]['auto_invoice_amount_tax'] + res[
                    invoice.id]['auto_invoice_amount_untaxed']
        return res

    _columns = {
        'transfer_entry_id': fields.many2one('account.move',
                                             'Transfer Entry',
                                             ondelete="set null"),
        'auto_invoice_id': fields.many2one('account.invoice',
                                           'Auto Invoice',
                                           ondelete="set null"),
        'auto_invoice_amount_untaxed': fields.function(
            _auto_invoice_amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Auto Invoice Subtotal', store=False, multi='auto_invoice_all'),
        'auto_invoice_amount_tax': fields.function(
            _auto_invoice_amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Auto Invoice Tax', store=False, multi='auto_invoice_all'),
        'auto_invoice_amount_total': fields.function(
            _auto_invoice_amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Auto Invoice Total', store=False, multi='auto_invoice_all'),
    }

    def _get_tax_relation(self, cr, uid, invoice_id, context=None):
        # ----- keep relation between tax and relative intra cee tax
        tax_relation = {}
        inv = self.browse(cr, uid, invoice_id, context)
        for line in inv.invoice_line:
            # ----- Check if tax has autoinvoice tax
            for tax in line.invoice_line_tax_id:
                tax_relation.update(
                    {tax.id: tax.auto_invoice_tax_id.id})
        return tax_relation

    def _get_partner(self, cr, uid, fiscal_position, invoice, context=None):
        
        if fiscal_position.use_same_partner:
            partner_id = invoice.partner_id.id
            if invoice.partner_id.property_account_receivable.type != 'view':
                prop_ar_id = invoice.partner_id.property_account_receivable.id
            else:
                raise orm.except_orm(
                    _('Error!'),
                    _('Property_account_receivable of partner "%s" can\'t be of type \'view\'. \
                    Verify if the partner is set properly as \'customer\'.')
                    % invoice.partner_id.name)
        else:
            if fiscal_position.auto_invoice_partner_id:
                partner_id = fiscal_position.auto_invoice_partner_id.id
                if fiscal_position.auto_invoice_partner_id.property_account_receivable.type != 'view':
                    prop_ar_id = fiscal_position.auto_invoice_partner_id.property_account_receivable.id
                else:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Property_account_receivable of partner "%s" can\'t be of type \'view\'. \
                        Verify if the partner is set properly as \'customer\'.')
                        % fiscal_position.auto_invoice_partner_id.name)
            else:
                raise orm.except_orm(
                    _('Error!'),
                    _('Missing partner in {fp} fiscal position.').format(fp=fiscal_position.name)
                )
        
        return partner_id, prop_ar_id

    def auto_invoice_vals(self, cr, uid, invoice_id, fiscal_position_id,
                          context=None):
        context = context or {}
        invoice = self.browse(cr, uid, invoice_id, context)
        fp_id = fiscal_position_id or invoice.fiscal_position.id
        fiscal_position = self.pool['account.fiscal.position'].browse(
            cr, uid, fp_id, context)

        partner_id, prop_ar_id = self._get_partner(cr, uid, fiscal_position, invoice, context)
        # ----- Get actual invoice copy
        copy_inv = self.copy_data(cr, uid, invoice_id, {}, context)
        if not copy_inv:
            return {}
        new_inv = copy_inv.copy()
        # ----- Change some data in new invoice
        new_inv.update({
            'type': invoice.type.replace('in_', 'out_'),
            'origin': invoice.number or '',
            'supplier_invoice_number': '',
            'internal_number': '',
            'number': '',
            'state': 'draft',
            'move_id': False,
            'partner_id': partner_id,
            'account_id': prop_ar_id,
            'journal_id': fiscal_position.journal_auto_invoice_id.id,
            'date_invoice': invoice.registration_date,
            'date_due': invoice.registration_date,
        })
        new_line = []
        tax_relation = self._get_tax_relation(cr, uid, invoice_id, context)
        if self.pool['ir.module.module'].search(cr, uid, [
            ('state', '=', 'installed'),
            ('name', '=', 'l10n_it_asset')], context=context):
            asset = True
        else:
            asset = False
        for line in new_inv['invoice_line']:
            vals = line[2].copy()
            vals['account_analytic_id'] = False
            # ----- Change account in new invoice line
            vals['account_id'] = fiscal_position.account_transient_id.id
            if asset:
                vals['asset_id'] = False
                vals['asset_category_id'] = False

            # ----- Change tax in new invoice line
            new_tax = []
            line_reverse_charge = False
            for tax in vals['invoice_line_tax_id']:
                tax_obj = self.pool['account.tax']
                auto_invoice_tax_id = tax_obj.browse(cr, uid, tax[2][0], context).auto_invoice_tax_id
                line_reverse_charge = True if auto_invoice_tax_id else False
                new_tax.append((6, 0, [tax_relation[tax[2][0]]]))
            vals['invoice_line_tax_id'] = new_tax
            if vals['invoice_line_tax_id'][0][2][0]:
                new_line.append((0, 0, vals))
            if not line_reverse_charge:
                del new_inv['invoice_line'][new_inv['invoice_line'].index(line)]
        new_inv['invoice_line'] = new_line
        return new_inv

    def extra_ue_auto_invoice_vals(self, cr, uid, invoice_id,
                                   fp_id, context=None):
        # ----- Get complete invoice copy
        res = self.auto_invoice_vals(cr, uid, invoice_id,
                                     fp_id, context)
        fiscal_position = self.pool['account.fiscal.position'].browse(
            cr, uid, fp_id, context)
        invoice = self.browse(cr, uid, invoice_id, context)
        res['partner_id'], prop_ar_id = self._get_partner(cr, uid, fiscal_position, invoice, context)
        
        # ----- Get right lines
        invoice = self.browse(cr, uid, invoice_id, context)
        fp_id = fp_id or invoice.fiscal_position.id
        fiscal_position = self.pool['account.fiscal.position'].browse(
            cr, uid, fp_id, context)
        product_obj = self.pool['product.product']
        total = 0.0
        for line in res['invoice_line']:
            product = line[2]['product_id'] and product_obj.browse(
                cr, uid, line[2]['product_id']) or False
            if product and product.type == 'service' or not product:
                price_subtotal = line[2]['price_unit'] * (
                    1 - (line[2]['discount'] or 0.0) / 100.0)
                total += price_subtotal * line[2]['quantity']
        if not total:
            return False
        res['invoice_line'] = [(0, 0, {
            'name': fiscal_position.extra_ue_line_detail,
            'price_unit': total,
            'quantity': 1,
            'account_id': prop_ar_id,
            'invoice_line_tax_id': [(6, 0, [fiscal_position.extra_ue_service_tax_id.id])]
        })]
        return res

    def create_auto_invoice(self, cr, uid, ids, context=None):
        context = context or {}
        new_invoice_ids = []
        move_obj = self.pool['account.move']
        wf_service = netsvc.LocalService("workflow")
        for inv in self.browse(cr, uid, ids, context):
            auto_invoice_to_be_reconciled = []
            invoice_to_be_reconciled = []
            # ----- Apply Auto Invoice only on supplier invoice/refund
            if not (inv.type == 'in_invoice' or inv.type == 'in_refund'):
                continue
            fiscal_position = inv.fiscal_position
            # ----- Check if fiscal positon is active for intra CEE invoice
            if not fiscal_position:
                continue

            if not (fiscal_position.active_reverse_charge or
                    fiscal_position.active_extra_ue_service):
                continue

            line_reverse_charge = False

            for line in inv.invoice_line:
                for tax in line.invoice_line_tax_id:
                    if tax.auto_invoice_tax_id:
                        line_reverse_charge = True

            if not line_reverse_charge:
                raise orm.except_orm(
                        _('Error!'),
                        _('You cannot create an invoice where tax {tax} have not set auto invoice tax').format(tax=line.invoice_line_tax_id[0].description))
                continue

            # ----- Get actual invoice copy based on fiscal position flag
            if fiscal_position.active_reverse_charge:
                new_inv = self.auto_invoice_vals(cr, uid, inv.id,
                                                 fiscal_position.id,
                                                 context)
            elif fiscal_position.active_extra_ue_service:
                new_inv = self.extra_ue_auto_invoice_vals(
                    cr, uid, inv.id, fiscal_position.id, context)
            if not new_inv:
                continue
            # ----- Create Auto Invoice...Yeah!!!!!
            auto_invoice_id = self.create(cr, uid, new_inv, context)
            new_invoice_ids.append(auto_invoice_id)
            # ----- Recompute taxes in new invoice
            self.button_reset_taxes(cr, uid, [auto_invoice_id], context)
            # ----- Validate invoice
            wf_service.trg_validate(uid, 'account.invoice',
                                    auto_invoice_id, 'invoice_open', cr)
            # ----- Get new values from auto invoice
            new_invoice = self.browse(cr, uid, auto_invoice_id, context)
            # get move_line_ids of auto invoice with partner-account_id partner for reconciliation
            for move_line in new_invoice.move_id.line_id:
                if move_line.account_id == move_line.partner_id.property_account_receivable:
                    auto_invoice_to_be_reconciled.append(move_line.id)
            # the same for supplier invoice
            for move_line in inv.move_id.line_id:
                if move_line.account_id == move_line.partner_id.property_account_payable and \
                        move_line.amount_residual == inv.amount_tax:
                    invoice_to_be_reconciled.append(move_line.id)
            # Create transfer entry movements
            account_move_line_vals = []
            # ----- Tax for supplier
            debit_1 = credit_1 = 0.0
            debit_2 = credit_2 = 0.0
            debit_3 = credit_3 = 0.0
            if inv.type == 'in_invoice':
                debit_1 = inv.auto_invoice_amount_tax
                debit_2 = inv.auto_invoice_amount_untaxed
                credit_3 = inv.auto_invoice_amount_total
            else:
                credit_1 = inv.auto_invoice_amount_tax
                credit_2 = inv.auto_invoice_amount_untaxed
                debit_3 = inv.auto_invoice_amount_total
            account_move_line_vals.append((0, 0, {
                'name': _('Tax for Supplier'),
                'debit': debit_1,
                'credit': credit_1,
                'partner_id': inv.partner_id.id,
                'account_id': inv.account_id.id,  # use actual account_id configured in invoice
                # if set, instead of generic partner_id.property_account_payable.id,
            }))
            # ----- Products values
            account_move_line_vals.append((0, 0, {
                'name': _(u'Products'),
                'debit': debit_2,
                'credit': credit_2,
                'partner_id': new_invoice.partner_id.id,
                'account_id': fiscal_position.account_transient_id.id,
            }))
            # ----- Invoice Total
            account_move_line_vals.append((0, 0, {
                'name': _(u'Invoice Total'),
                'debit': debit_3,
                'credit': credit_3,
                'partner_id': new_invoice.partner_id.id,
                'account_id': new_invoice.partner_id.property_account_receivable.id,
            }))
            # ----- Account Move
            account_move_vals = {
                'name': '/',
                'state': 'draft',
                'journal_id': fiscal_position.journal_transfer_entry_id.id,
                'line_id': account_move_line_vals,
                'date': inv.registration_date,
                'period_id': inv.period_id.id,
            }
            context.update({'date': inv.registration_date})
            
            transfer_entry_id = move_obj.create(
                cr, uid, account_move_vals, context)
            move_obj.post(cr, uid, [transfer_entry_id], context)
            # Link the transfer entry move and auto invoice to supplier invoice
            self.write(cr, uid, [inv.id],
                       {'auto_invoice_id': auto_invoice_id,
                        'transfer_entry_id': transfer_entry_id})
            # get move_line_ids of auto invoice with partner-account_id partner for reconciliation
            move = move_obj.browse(cr, uid, [transfer_entry_id], context)[0]
            for move_line in move.line_id:
                if move_line.account_id == move_line.partner_id.property_account_receivable:
                    auto_invoice_to_be_reconciled.append(move_line.id)
                if move_line.account_id == move_line.partner_id.property_account_payable:
                    invoice_to_be_reconciled.append(move_line.id)
            account_move_line_obj = self.pool['account.move.line']
            account_move_line_obj.reconcile_partial(cr, uid, auto_invoice_to_be_reconciled, context=context)
            account_move_line_obj.reconcile_partial(cr, uid, invoice_to_be_reconciled, context=context)

        return new_invoice_ids

    def action_number(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).action_number(cr, uid,
                                                         ids, context)
        self.create_auto_invoice(cr, uid, ids, context)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        account_move = self.pool['account.move']
        voucher_obj = self.pool['account.voucher']
        wf_service = netsvc.LocalService("workflow")
        move_ids = []
        for inv in self.browse(cr, uid, ids, context):
            # ----- Delete Auto Invoice
            if inv.auto_invoice_id:
                # ----- Delete Payments for supplier invoice
                if len(inv.payment_ids) > 1:
                    raise orm.except_orm(
                        _('Error!'),
                        _('You cannot cancel an invoice which is partially \
                        paid. You need to unreconcile related payment entries \
                        first.'))
                reconcile_ids = []
                for payment in inv.auto_invoice_id.payment_ids:
                    if payment.reconcile_id:
                        reconcile_ids.append(payment.reconcile_id.id)
                    if payment.reconcile_partial_id:
                        reconcile_ids.append(payment.reconcile_partial_id.id)

                # ----- Delete Payments for auto invoice
                if inv.transfer_entry_id:
                    for move in inv.transfer_entry_id.line_id:
                        if move.reconcile_id:
                            reconcile_ids.append(move.reconcile_id.id)
                        if move.reconcile_partial_id:
                            reconcile_ids.append(move.reconcile_partial_id.id)

                if reconcile_ids:
                    self.pool['account.move.reconcile'].unlink(cr, uid, list(set(reconcile_ids)), context)

                # ---- Delete Invoice
                wf_service.trg_validate(uid, 'account.invoice',
                                        inv.auto_invoice_id.id,
                                        'invoice_cancel', cr)
                self.action_cancel_draft(cr, uid, [inv.auto_invoice_id.id])
                self.write(cr, uid, [inv.auto_invoice_id.id], {'internal_number': False}, context)
                self.unlink(cr, uid, [inv.auto_invoice_id.id], context)
            # ----- Save account move ids
            if inv.transfer_entry_id:
                move_ids.append(inv.transfer_entry_id.id)
        # ----- Reopen and delete account move
        if move_ids:
            account_move.button_cancel(cr, uid, move_ids, context)
            account_move.unlink(cr, uid, move_ids, context)
        return super(account_invoice, self).action_cancel(
            cr, uid, ids, context)

    def action_move_create(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        ait_obj = self.pool['account.invoice.tax']
        if isinstance(ids, (int, long)):
            ids = [ids]
        for inv in self.browse(cr, uid, ids, context=context):
            amount_tax = context.get('amount_tax', 0.0)
            if not amount_tax:
                compute_taxes = ait_obj.compute(cr, uid, inv.id, context=context)
                for tax in compute_taxes:
                    amount_tax += compute_taxes[tax]['amount']

            if inv.fiscal_position.active_reverse_charge and inv.type in ['in_invoice', 'in_refund']:
                context.update({'amount_tax': amount_tax, 'reverse_charge': True})
            else:
                context.update({'amount_tax': amount_tax})
            super(account_invoice, self).action_move_create(cr, uid, [inv.id], context=context)

        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'transfer_entry_id': '', 'auto_invoice_id': ''})
        return super(account_invoice, self).copy(cr, uid, id, default, context)
