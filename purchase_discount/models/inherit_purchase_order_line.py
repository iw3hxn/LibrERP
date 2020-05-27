# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012 Pexego Sistemas Informáticos (<http://tiny.be>).
#    Copyright (C) 2020 Didotech S.r.l. (<http://www.didotech.com/>).
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
            product_uom_obj = self.pool['product.uom']

            product = product_obj.browse(cr, uid, product_id, context)
            price = product.cost_price

            rule_id = res_dict.get(pricelist_id) and res_dict[pricelist_id][1] or False
            if rule_id:
                item_base = item_obj.read(cr, uid, [rule_id], ['base'])[0]['base']
                if item_base > 0:
                    field_name = price_type_obj.browse(cr, uid, item_base, context).field
                    price = product[field_name]

                    if uom and uom != product.uom_id.id:
                        # the unit price is in a different uom
                        factor = product_uom_obj._compute_qty(cr, uid, uom, 1.0, product.uom_id.id)
                    else:
                        factor = 1.0

                    price *= factor

                elif item_base == -2:
                    # _logger.debug('Checking item base is -2')
                    if context.get('partner_id', False):
                        for seller in product.seller_ids:
                            if seller.name.id == context['partner_id']:
                                qty_in_seller_uom = qty
                                seller_uom = seller.product_uom.id
                                if uom != seller_uom:
                                    qty_in_seller_uom = product_uom_obj._compute_qty(cr, uid, uom, qty, to_uom_id=seller_uom)

                                for line in seller.pricelist_ids:
                                    if line.min_quantity <= qty_in_seller_uom:
                                        price = line.price
                                        # price = seller.pricelist_ids[0].price
                    else:
                        price = product.seller_ids[0].pricelist_ids[0].price
                    # not supported:
                    # elif item_base == -1:

            # if uom and uom != product.uom_id.id:
            #     # the unit price is in a different uom
            #     factor = product_uom_obj._compute_qty(cr, uid, uom, 1.0, product.uom_id.id)
            # else:
            #     factor = 1.0

            return price

        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        
        res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, notes, context)

        context = {'lang': context.get('lang'), 'partner_id': partner_id}
        result = res['value']
        pricelist_obj = self.pool['product.pricelist']
        product_obj = self.pool['product.product']
        
        if product_id and pricelist_id:
            if result.get('price_unit', False):
                price = result['price_unit']
            else:
                return res
            uom = result.get('product_uom', uom_id)
            product = product_obj.browse(cr, uid, product_id, context)
            list_price = pricelist_obj.price_rule_get(cr, uid, [pricelist_id],
                    product.id, qty or 1.0, partner_id, {'uom': uom_id, 'date': date_order})

            po_pricelist = pricelist_obj.browse(cr, uid, pricelist_id, context=context)
            result['rules'] = list_price[pricelist_id][1]
            new_list_price = get_real_price(list_price, product_id, qty, uom, pricelist_id)
            if po_pricelist.visible_discount and list_price[pricelist_id][0] != 0 and new_list_price != 0:
                # if product.company_id and po_pricelist.currency_id.id != product.company_id.currency_id.id:
                #     # new_list_price is in company's currency while price is in pricelist currency
                #     ctx = context.copy()
                #     ctx['date'] = date_order
                #     new_list_price = self.pool['res.currency'].compute(
                #         cr, uid,
                #         product.company_id.currency_id.id,
                #         po_pricelist.currency_id.id,
                #         new_list_price, context=ctx
                #     )

                discount = (new_list_price - price) / new_list_price * 100
                if discount >= 0:
                    result['price_unit'] = new_list_price
                    result['discount'] = discount

        return res

    def _amount_line(self, cr, uid, ids, prop, unknown_none, unknow_dict):
        res = {}
        cur_obj = self.pool['res.currency']
        for line in self.browse(cr, uid, ids):
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur,
                                         line.price_unit * line.product_qty * (1 - (line.discount or 0.0) / 100.0))
        return res

    _columns = {
        'discount': fields.float('Discount (%)', digits=(3, 2)),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute=dp.get_precision('Purchase Price')),
    }

    _defaults = {
        'discount': lambda *a: 0.0,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

