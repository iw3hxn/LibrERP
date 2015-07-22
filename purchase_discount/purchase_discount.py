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
import logging

from openerp.osv import orm, fields
import decimal_precision as dp

_logger = logging.getLogger(__name__)



class purchase_order_line(orm.Model):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, notes=False, context=None):
        
        def get_real_price(res_dict, product_id, qty, uom, pricelist):

            _logger.debug('Getting real price')
            """Retrieve the price before applying the pricelist"""
            item_obj = self.pool['product.pricelist.item']
            price_type_obj = self.pool['product.price.type']
            product_obj = self.pool['product.product']

            product = product_obj.browse(cr, uid, product_id, context)
            price = product.cost_price

            rule_id = res_dict.get(pricelist_id) and res_dict[pricelist_id][1] or False
            if rule_id:
                item_base = item_obj.read(cr, uid, [rule_id], ['base'])[0]['base']
                if item_base > 0:
                    field_name = price_type_obj.browse(cr, uid, item_base).field
                    product_read = product_obj.read(cr, uid, product_id, [field_name], context=context)
                    price = product_read[field_name]
                elif item_base == -2:
                    _logger.debug('Checking item base is -2')
                    price = product.seller_ids[0].pricelist_ids[0].price
                    # not supported:
                    # elif item_base == -1:

            factor = 1.0
            if uom and uom != product.uom_id.id:
                # the unit price is in a different uom
                factor = self.pool['product.uom']._compute_qty(cr, uid, uom, 1.0, product.uom_id.id)
            return price * factor

        if not context:
            context = {}
        
        res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, notes, context)
        

        context = {'lang': context.get('lang'), 'partner_id': partner_id}
        result = res['value']
        pricelist_obj = self.pool['product.pricelist']
        product_obj = self.pool['product.product']
        
        if product_id:
            if result.get('price_unit', False):
                price = result['price_unit']
            else:
                return res
            uom = result.get('product_uom', uom_id)
            product = product_obj.browse(cr, uid, product_id, context)
            list_price = pricelist_obj.price_rule_get(cr, uid, [pricelist_id],
                    product.id, qty or 1.0, partner_id, {'uom': uom_id, 'date': date_order})

            so_pricelist = pricelist_obj.browse(cr, uid, pricelist_id, context=context)

            new_list_price = get_real_price(list_price, product_id, qty, uom, pricelist_id)
            if so_pricelist.visible_discount and list_price[pricelist_id][0] != 0 and new_list_price != 0:
                if product.company_id and so_pricelist.currency_id.id != product.company_id.currency_id.id:
                    # new_list_price is in company's currency while price in pricelist currency
                    ctx = context.copy()
                    ctx['date'] = date_order
                    new_list_price = self.pool['res.currency'].compute(cr, uid,
                                                                       product.company_id.currency_id.id,
                                                                       so_pricelist.currency_id.id,
                                                                       new_list_price, context=ctx)
                discount = (new_list_price - price) / new_list_price * 100
                if discount > 0:
                    result['price_unit'] = new_list_price
                    result['discount'] = discount
        return res


    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur,
                                         line.price_unit * line.product_qty * (1 - (line.discount or 0.0) / 100.0))
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

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
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
                val1 += line.price_subtotal
                for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit * (
                    1 - (line.discount or 0.0) / 100.0), line.product_qty, line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
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
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Purchase Price'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Purchase Price'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The total amount"),
    }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        if context is None: context = {}

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

