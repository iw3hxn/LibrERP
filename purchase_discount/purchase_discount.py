# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012 Pexego Sistemas Informáticos (<http://tiny.be>).
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
from openerp.osv import orm, fields


class purchase_order_line(orm.Model):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        cur_obj = self.pool['res.currency']
        for line in self.browse(cr, uid, ids):
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, line.price_unit * line.product_qty * (1 - (line.discount or 0.0) / 100.0))
        return res
    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, notes=False, context=None):
        
        def get_real_price(res_dict, product_id, qty, uom, pricelist):
            item_obj = self.pool['product.pricelist.item']
            price_type_obj = self.pool['product.price.type']
            product_obj = self.pool['product.product']
            template_obj = self.pool['product.template']
            field_name = 'list_price'

            if res_dict.get('item_id', False) and res_dict['item_id'].get(pricelist, False):
                item = res_dict['item_id'].get(pricelist, False)
                item_base = item_obj.read(cr, uid, [item], ['base'])[0]['base']
                if item_base > 0:
                    field_name = price_type_obj.browse(cr, uid, item_base).field

            product = product_obj.browse(cr, uid, product_id, context)
            product_tmpl_id = product.product_tmpl_id.id

            product_read = template_obj.read(cr, uid, product_tmpl_id, [field_name], context)

            factor = 1.0
            if uom and uom != product.uom_id.id:
                product_uom_obj = self.pool['product.uom']
                uom_data = product_uom_obj.browse(cr, uid, product.uom_id.id, context)
                factor = uom_data.factor
            return product_read[field_name] * factor
        
        res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, notes, context)
        
        
        context = {'partner_id': partner_id}
        result = res['value']
        pricelist_obj = self.pool['product.pricelist']
        product_obj = self.pool['product.product']
        
        if product_id:
            if result.get('price_unit', False):
                price = result['price_unit']
            else:
                return res

            product = product_obj.browse(cr, uid, product_id, context)
            list_price = pricelist_obj.price_get(cr, uid, [pricelist_id],
                    product.id, qty or 1.0, partner_id, {'uom': uom_id, 'date': date_order,})

            pricelists = pricelist_obj.read(cr, uid, [pricelist_id], ['visible_discount'])

            new_list_price = get_real_price(list_price, product.id, qty, uom_id, pricelist_id)

            if len(pricelists) > 0 and pricelists[0]['visible_discount'] and list_price[pricelist_id] != 0:
                discount = (new_list_price - price) / new_list_price * 100
                result['price_unit'] = new_list_price
                result['discount'] = discount
            else:
                result['discount'] = 0.0
                
        return res

    _columns = {
        'discount': fields.float('Discount (%)', digits=(3, 2)),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
    }

    _defaults = {
        'discount': lambda *a: 0.0,
    }


class purchase_order(orm.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context):
        res = {}
        cur_obj = self.pool['res.currency']
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                for c in self.pool.get('account.tax').compute(cr, uid, line.taxes_id, line.price_unit * (1 - (line.discount or 0.0) / 100.0), line.product_qty, order.partner_address_id.id, line.product_id, order.partner_id):
                    val += c['amount']
                val1 += line.price_subtotal
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool['purchase.order.line'].browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Purchase Price'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax"),
        'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The total amount"),
    }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        if context is None:
            context = {}
        res = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context=context)

        res.update({'discount': order_line.discount or 0.0,
                    'price_unit': order_line.price_unit, })
        return res

    def _get_price_unit_invoice(self, cursor, user, move_line, type):

        res = super(stock_picking, self)._get_price_unit_invoice(cursor, user, move_line, type)

        if move_line.purchase_line_id:
            res.update({'discount': move_line.purchase_line_id.discount or 0.0, })
        return res

class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        if move_line.purchase_line_id:
            self.pool['account.invoice.line'].write(cr, uid, [invoice_line_id], {
                'discount': move_line.purchase_line_id.discount,
                })
        return super( stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

