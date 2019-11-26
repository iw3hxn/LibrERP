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

from openerp import pooler
from openerp.addons import base
from openerp.osv import orm, fields
from openerp.tools.translate import _


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    def get_precision_tax():
        def change_digit_tax(cr):
            res = pooler.get_pool(cr.dbname).get('decimal.precision').precision_get(cr, 1, 'Account')
            return (17, res + 3)

        return change_digit_tax

    def _get_tax_list(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            tax_list = []
            for tax in line.invoice_line_tax_id:
                if tax.description:
                    tax_list.append(tax.description)
            res[line.id] = ','.join(tax_list)
        return res

    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute=get_precision_tax()),
        'origin_document': fields.reference(_('Reference'), selection=base.res.res_request._links_get, size=None),
        'tax_list': fields.function(_get_tax_list, type='text', string='Tax Code'),
    }

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        sale_order_line_obj = self.pool['sale.order.line']
        sale_order_line_ids = []
        for line in self.browse(cr, uid, ids, context):
            if line.origin_document and line.origin_document._name == 'sale.order.line':
                sale_order_line_ids += sale_order_line_obj.search(cr, uid, [('id', '=', line.origin_document.id)], context=context)
                # the invoice line is create directly form sale order.line
        if sale_order_line_ids:
            sale_order_line_obj.write(cr, uid, sale_order_line_ids, {'invoiced': False}, context)
        return super(account_invoice_line, self).unlink(cr, uid, ids, context=context)

    def onchange_account_id(self, cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id):
        if not account_id:
            return {}
        context = self.pool['res.users'].context_get(cr, uid)
        unique_tax_ids = []
        fpos = fposition_id and self.pool['account.fiscal.position'].browse(cr, uid, fposition_id, context) or False
        account = self.pool['account.account'].browse(cr, uid, account_id, context)
        if not product_id:
            taxes = account.tax_ids
            # se non trovo le tasse nel conto esco
            if not taxes:
                return {'value': {}}
            unique_tax_ids = self.pool['account.fiscal.position'].map_tax(cr, uid, fpos, taxes)
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
                    account_id = self.pool['product.product'].default_get(cr, uid, ['property_account_income'])[
                                     'property_account_income'] or self.pool['product.category'].default_get(cr, uid, ['property_account_income_categ'])[
                                     'property_account_income_categ']

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
                    taxes = self.pool['product.product'].default_get(cr, uid, ['supplier_taxes_id']).get(
                        'supplier_taxes_id', False)
                    if taxes:
                        taxes = self.pool['account.tax'].browse(cr, uid, taxes, context)
                    account_id = self.pool['product.product'].default_get(cr, uid, ['property_account_expense'])[
                                     'property_account_expense'] or self.pool['product.category'].default_get(cr, uid, ['property_account_expense_categ'])[
                                     'property_account_expense_categ']

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
