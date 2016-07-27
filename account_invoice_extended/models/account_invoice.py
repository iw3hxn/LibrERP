# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp import pooler
from openerp.tools.translate import _


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    # def _get_sale_order(self, cr, uid, ids, field_name, model_name, context=None):
    #     result = {}
    #     crm_lead_obj = self.pool['crm.lead']
    #     sale_order_obj = self.pool['sale.order']
    #
    #     for crm_lead in crm_lead_obj.browse(cr, uid, ids, context):
    #         partner_id = crm_lead.partner_id.id
    #         contact_id = crm_lead.partner_address_id.id
    #         if contact_id:
    #             result[crm_lead.id] = sale_order_obj.search(cr, uid, [('partner_id', '=', partner_id), ('partner_order_id', '=', contact_id)])
    #         else:
    #             result[crm_lead.id] = sale_order_obj.search(cr, uid, [('partner_id', '=', partner_id)])
    #     return result

    def _get_stock_picking(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        stock_picking_obj = self.pool['stock.picking']

        for invoice in self.browse(cr, uid, ids, context):
            origins = {}

            for line in invoice.invoice_line:
                line_origin = line.origin or False
                if line_origin not in origins:
                    origins[line_origin] = invoice.id
            if invoice.origin:
                for invoice_origin in invoice.origin.split(', '):
                    if invoice_origin not in origins:
                        origins[invoice_origin] = invoice.id
            picking_ids = []
            for origin in origins:
                if origin:
                    # OUTxxx:SOyy
                    if len(origin.split(':')) == 2:
                        pickings_name = origin.split(':')[0]
                    else:
                        pickings_name = origin
                    picking_ids += stock_picking_obj.search(cr, uid, [('name', '=', pickings_name)], context=context)
                    print picking_ids

            result[invoice.id] = picking_ids

        return result

    _columns = {
        'supplier_invoice_number': fields.char('Supplier invoice nr', size=16),
        # 'sale_order_ids': fields.function(_get_sale_order, 'Sale Order', type='one2many', relation="sale.order", readonly=True, method=True),
        'stock_picking_ids': fields.function(_get_stock_picking, 'Stock Picking', type='one2many', relation="stock.picking", readonly=True, method=True),
    }
    
    def copy(self, cr, uid, order_id, defaults, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        defaults['user_id'] = uid
        return super(account_invoice, self).copy(cr, uid, order_id, defaults, context)

    def invoice_validate_check(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.type == 'out_invoice' and invoice.fiscal_position and invoice.fiscal_position.sale_journal_id and invoice.fiscal_position.sale_journal_id != invoice.journal_id:
                raise orm.except_orm(_('Fattura Cliente'),
                    _('Impossibile to valide invoice of {partner} because journal on invoive \'{invoice_journal}\' is different from journal \'{fiscal_position_journal}\' set on fiscal position \'{invoice_fiscal_position}\'').format(
                        partner=invoice.partner_id.name, invoice_journal=invoice.journal_id.name, fiscal_position_journal=invoice.fiscal_position.sale_journal_id.name, invoice_fiscal_position=invoice.fiscal_position.name))
                return False
        return True

    def invoice_cancel_check(self, cr, uid, ids, context=None):
        return True

    def invoice_proforma_check(self, cr, uid, ids, context=None):
        return True

    def onchange_fiscal_position(self, cr, uid, ids, journal_id, fiscal_position, ttype, context=None):

        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if not fiscal_position:
            return False

        fpos_obj = self.pool['account.fiscal.position']
        new_fiscal_position = fpos_obj.browse(cr, uid, fiscal_position, context)
        if ttype in ['out_invoice']:
            journal_id = new_fiscal_position.sale_journal_id and new_fiscal_position.sale_journal_id.id or journal_id
        elif ttype in ['in_invoice']:
            journal_id = new_fiscal_position.purchase_journal_id and new_fiscal_position.purchase_journal_id.id or journal_id

        # if is an exiting invoice, also change tax inside line to new fiscal position

        warning = {}
        for inv in self.browse(cr, uid, ids, context):
            if inv.fiscal_position != new_fiscal_position:
                for line in inv.invoice_line:
                    if line.product_id:
                        new_taxes = fpos_obj.map_tax(cr, uid, new_fiscal_position, line.product_id.taxes_id)
                        line.write({'invoice_line_tax_id': [(6, 0, new_taxes)]})
                inv.button_reset_taxes()
                warning = {
                    'title': _('Fiscal Position'),
                    'message': _('Is Change from \n{old_fiscal_position} to \n{new_fiscal_position}: \nPlease Press Button for recalculate tax').format(
                        old_fiscal_position=inv.fiscal_position and inv.fiscal_position.name or _('None'), new_fiscal_position=new_fiscal_position.name)
                }

        return {'value': {'journal_id': journal_id}, 'warning': warning}

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        # adaptative function: the system learn
        invoice_id = super(account_invoice, self).create(cr, uid, vals, context=context)
        # create function return only 1 id

        if set(vals.keys()).intersection(['carriage_condition_id', 'goods_description_id', 'payment_term']):
            invoice = self.browse(cr, uid, invoice_id, context)
            partner_vals = {}
            if not invoice.partner_id.carriage_condition_id:
                partner_vals['carriage_condition_id'] = vals.get('carriage_condition_id')
            if not invoice.partner_id.goods_description_id:
                partner_vals['goods_description_id'] = vals.get('goods_description_id')
            if not invoice.partner_id.property_payment_term:
                partner_vals['property_payment_term'] = vals.get('payment_term')
            if partner_vals:
                invoice.partner_id.write(partner_vals)

        return invoice_id

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        if not ids:
            return True

        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)

        if isinstance(ids, (int, long)):
            ids = [ids]

        for invoice in self.browse(cr, uid, ids, context=context):
            # adaptative function: the system learn
            if set(vals.keys()).intersection(['carriage_condition_id', 'goods_description_id', 'payment_term']):
                partner_vals = {}
                if not invoice.partner_id.carriage_condition_id:
                    partner_vals['carriage_condition_id'] = vals.get('carriage_condition_id')
                if not invoice.partner_id.goods_description_id:
                    partner_vals['goods_description_id'] = vals.get('goods_description_id')
                if not invoice.partner_id.property_payment_term:
                    partner_vals['property_payment_term'] = vals.get('payment_term')
                if partner_vals:
                    invoice.partner_id.write(partner_vals)

        return res

    # def button_change_fiscal_position(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = self.pool['res.users'].context_get(cr, uid)
    #
    #     fpos_obj = self.pool['account.fiscal.position']
    #
    #     for inv in self.browse(cr, uid, ids, context):
    #         for line in inv.invoice_line:
    #             if line.product_id:
    #                 new_taxes = fpos_obj.map_tax(cr, uid, inv.fiscal_position, line.product_id.taxes_id)
    #                 line.write({'invoice_line_tax_id': [(6, 0, new_taxes)]})
    #         inv.button_reset_taxes()
    #
    #     return True

    # override to group product_id too
    def inv_line_characteristic_hashcode(self, invoice, invoice_line):
        """Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""
        return "%s-%s-%s-%s"%(
            invoice_line['account_id'],
            invoice_line.get('tax_code_id', "False"),  # invoice_line.get('product_id',"False"),
            invoice_line.get('analytic_account_id', "False"),
            invoice_line.get('date_maturity', "False"))

    # override to merge description (after will be trunked to x character everyway)
    def group_lines(self, cr, uid, iml, line, inv):
        """Merge account move lines (and hence analytic lines) if invoice line hashcodes are equals"""
        if inv.journal_id.group_invoice_lines:
            line2 = {}
            for x, y, l in line:
                tmp = self.inv_line_characteristic_hashcode(inv, l)

                if tmp in line2:
                    am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
                    line2[tmp]['debit'] = (am > 0) and am or 0.0
                    line2[tmp]['credit'] = (am < 0) and -am or 0.0
                    line2[tmp]['tax_amount'] += l['tax_amount']
                    line2[tmp]['analytic_lines'] += l['analytic_lines']
                    line2[tmp]['amount_currency'] += l['amount_currency']
                    line2[tmp]['quantity'] += l['quantity']
                    line2[tmp]['name'] += l['name']
                else:
                    line2[tmp] = l
            line = []
            for key, val in line2.items():
                line.append((0, 0, val))
        return line

    def unlink(self, cr, uid, ids, context=None):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        # account_invoice_line_obj = self.pool['account.invoice.line']
        stock_picking_obj = self.pool['stock.picking']
        origins = {}
        for invoice in self.browse(cr, uid, ids, context):
            for line in invoice.invoice_line:
                line_origin = line.origin or False
                if line_origin not in origins:
                    origins[line_origin] = invoice.id
            if invoice.origin:
                for invoice_origin in invoice.origin.split(', '):
                    if invoice_origin not in origins:
                        origins[invoice_origin] = invoice.id

        # now on origins i have all the origin and invoice.id
        for origin in origins:
            if origin:
                # OUTxxx:SOyy
                if len(origin.split(':')) == 2:
                    pickings_name = origin.split(':')[0]
                else:
                    pickings_name = origin
                picking_id = stock_picking_obj.search(cr, uid, [('name', '=', pickings_name)], context=context)
                if super(account_invoice, self).unlink(cr, uid, [origins[origin]], context=context):
                    if picking_id:
                        stock_picking_obj.write(cr, uid, [picking_id[0]], {'invoice_state': '2binvoiced'}, context=context)
                # now i need to eliminate other ids
                if origins[origin] in ids:
                    del ids[ids.index(origins[origin])]

        return super(account_invoice, self).unlink(cr, uid, ids, context=context)


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    def get_precision_tax():
        def change_digit_tax(cr):
            res = pooler.get_pool(cr.dbname).get('decimal.precision').precision_get(cr, 1, 'Account')
            return (17, res+3)
        return change_digit_tax

    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute=get_precision_tax()),
    }

    def onchange_account_id(self, cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id):
        if not account_id:
            return {}
        unique_tax_ids = []
        fpos = fposition_id and self.pool.get('account.fiscal.position').browse(cr, uid, fposition_id) or False
        account = self.pool.get('account.account').browse(cr, uid, account_id)
        if not product_id:
            taxes = account.tax_ids
            # se non trovo le tasse nel conto esco
            if not taxes:
                return {'value': {}}
            unique_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)
        else:
            # force user choosen account in context to allow product_id_change()
            # to fallback to the this accounts in case product has no taxes defined.
            context = {'account_id': account_id}
            product_change_result = self.product_id_change(cr, uid, ids, product_id, False, type=inv_type,
                                                           partner_id=partner_id, fposition_id=fposition_id,
                                                           context=context,
                                                           company_id=account.company_id.id)
            if product_change_result and 'value' in product_change_result and 'invoice_line_tax_id' in \
                    product_change_result['value']:
                unique_tax_ids = product_change_result['value']['invoice_line_tax_id']
        return {'value': {'invoice_line_tax_id': unique_tax_ids}}

    def default_get(self, cr, uid, fields, context=None):
        """
        """
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        res = super(account_invoice_line, self).default_get(cr, uid, fields, context=context)
        if not res.get('invoice_line_tax_id', False):
            fpos_obj = self.pool['account.fiscal.position']
            if context.get('type', False):
                if context['type'] in ['out_invoice', 'out_refund']:

                    taxes = self.pool['product.product'].default_get(cr, uid, ['taxes_id']).get('taxes_id', False)
                    if taxes:
                        taxes = self.pool['account.tax'].browse(cr, uid, taxes, context)
                    account_id = self.pool['product.product'].default_get(cr, uid, ['property_account_income'])['property_account_income'] or \
                                 self.pool['product.category'].default_get(cr, uid, ['property_account_income_categ'])['property_account_income_categ']

                    if context.get('fiscal_position', False):
                        fpos = fpos_obj.browse(cr, uid, context['fiscal_position'], context)
                        if taxes:
                            tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
                        else:
                            tax_id = []
                        account_id = fpos_obj.map_account(cr, uid, fpos, account_id)
                    else:
                        if taxes:
                            tax_id = [line.id for line in taxes]
                        else:
                            tax_id = []

                    res.update({
                        'invoice_line_tax_id': [(6, 0, tax_id)],
                        'account_id': account_id,
                    })
                if context['type'] in ['in_invoice', 'in_refund']:
                    taxes = self.pool['product.product'].default_get(cr, uid, ['supplier_taxes_id']).get('supplier_taxes_id', False)
                    if taxes:
                        taxes = self.pool['account.tax'].browse(cr, uid, taxes, context)
                    account_id = self.pool['product.product'].default_get(cr, uid, ['property_account_expense'])['property_account_expense'] or \
                                 self.pool['product.category'].default_get(cr, uid, ['property_account_expense_categ'])['property_account_expense_categ']

                    if context.get('fiscal_position', False):
                        fpos = fpos_obj.browse(cr, uid, context['fiscal_position'], context)
                        if taxes:
                            tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
                        else:
                            tax_id = []
                        account_id = fpos_obj.map_account(cr, uid, fpos, account_id)
                    else:
                        if taxes:
                            tax_id = [line.id for line in taxes]
                        else:
                            tax_id = []

                    res.update({
                        'invoice_line_tax_id': [(6, 0, tax_id)],
                        'account_id': account_id,
                    })

        return res