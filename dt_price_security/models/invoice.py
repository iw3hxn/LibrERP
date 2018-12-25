# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
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

import decimal_precision as dp
from openerp.osv import fields
from openerp.osv import orm


class account_invoice_line(orm.Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    def _get_user_can_modify(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        group_obj = self.pool['res.groups']

        if group_obj.user_in_group(cr, uid, uid, 'dt_price_security.can_modify_prices', context=context):
            flag = True
        else:
            flag = False

        for i in ids:
            res[i] = flag
        return res

    _columns = {
        'price_unit_copy': fields.related('price_unit', type="float", readonly=True, store=False, string='Unit Price', digits_compute= dp.get_precision('Account')),
        'user_can_modify_prices': fields.function(_get_user_can_modify, type='boolean',
                                                  string='User Can modify prices'),
        'product_can_modify_prices': fields.related('product_id', 'can_modify_prices', type='boolean',
                                                    string='Product Can modify prices'),
    }

    def onchange_price_unit(self, cr, uid, ids, product_id, price_unit, context=None):
        return {'value': {'price_unit_copy': price_unit}}

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid, context=context)
        if vals.get('discount', False) and not (context.get('active_model', False) == 'stock.picking'):
            if self.check_invoice_type(cr, uid, False, vals, context=context):
                self.check_discount_constrains(cr, uid, False, vals, context=context)
        return super(account_invoice_line, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid, context=context)
        if not isinstance(ids, list):
            ids = [ids]
        if vals.get('discount', False) and not (context.get('active_model', False) == 'stock.picking'):
            for line_id in ids:
                if self.check_invoice_type(cr, uid, line_id, vals, context=context):
                    self.check_discount_constrains(cr, uid, line_id, vals, context=context)

        return super(account_invoice_line, self).write(cr, uid, ids, vals, context=context)

    def check_invoice_type(self, cr, uid, line_id, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid, context=context)
        ret = False

        invoice_id = vals.get('invoice_id', False)
        inv_type = vals.get('type', False)

        if invoice_id:
            invoice_obj = self.pool['account.invoice']
            invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
            if isinstance(invoice, list):
                invoice = invoice[0]
            inv_type = invoice.type
        elif line_id:
            line_obj = self.pool['account.invoice.line']
            line = line_obj.browse(cr, uid, line_id, context=context)
            if isinstance(line, list):
                line = line[0]
            inv_type = line.invoice_id.type

        if inv_type == 'out_invoice' or inv_type == 'out_refund':
            ret = True
        return ret

    def check_discount_constrains(self, cr, uid, line_id, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid, context=context)

        discount = vals.get('discount', False)
        company_id = vals.get('company_id', False)
        pricelist = self.get_invoice_pricelist(cr, uid, line_id, vals, context=context)

        if discount:
            restriction_obj = self.pool['price_security.discount_restriction']
            restriction_obj.check_discount_with_restriction(cr, uid, discount, pricelist.id, company_id, context=context)
        return True

    def get_invoice_pricelist(self, cr, uid, line_id, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid, context=context)
        pricelist = False

        invoice_id = vals.get('invoice_id', False)

        if invoice_id:
            invoice_obj = self.pool['account.invoice']
            invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
            if isinstance(invoice, list):
                invoice = invoice[0]
            if invoice.partner_id.property_product_pricelist:
                pricelist = invoice.partner_id.property_product_pricelist
        elif line_id:
            line_obj = self.pool['account.invoice.line']
            line = line_obj.browse(cr, uid, line_id, context=context)
            if isinstance(line, list):
                line = line[0]
            if line.invoice_id.partner_id.property_product_pricelist:
                pricelist = line.invoice_id.partner_id.property_product_pricelist
            # for case when creating invice from sale order
        else:
            partner_obj = self.pool['res.partner']
            partner = partner_obj.browse(cr, uid, vals.get('partner_id', False), context=context)
            if isinstance(partner, list):
                partner = partner[0]
            if partner.property_product_pricelist:
                pricelist = partner.property_product_pricelist
        return pricelist

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False, address_invoice_id=False, currency_id=False,
                          context=None,
                          company_id=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid, context=context)
        ret = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty=qty, name=name,
                                                                  type=type,
                                                                  partner_id=partner_id, fposition_id=fposition_id,
                                                                  price_unit=price_unit,
                                                                  address_invoice_id=address_invoice_id,
                                                                  currency_id=currency_id, context=context,
                                                                  company_id=company_id)

        if not product:
            return ret

        product_obj = self.pool['product.product']
        product = product_obj.browse(cr, uid, product, context=context)
        if isinstance(product, list):
            product = product[0]

        group_obj = self.pool['res.groups']
        if group_obj.user_in_group(cr, uid, uid, 'dt_price_security.can_modify_prices', context=context):
            ret['value']['user_can_modify_prices'] = True
        else:
            ret['value']['user_can_modify_prices'] = False

        if product.can_modify_prices:
            ret['value']['product_can_modify_prices'] = True
        else:
            ret['value']['product_can_modify_prices'] = False

        return ret







