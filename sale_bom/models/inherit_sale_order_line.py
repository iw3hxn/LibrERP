# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2013-2014 Didotech srl (info at didotech.com)
#                          All Rights Reserved.
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
###############################################################################

from openerp.osv import orm, fields
import decimal_precision as dp
from openerp import tools


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    
    _columns = {
        'mrp_bom': fields.one2many('sale.order.line.mrp.bom', 'order_id', 'Bom Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'with_bom': fields.boolean(string='With BOM'),
        'cost_price_unit_routing': fields.float('Cost Price Routing', digits_compute=dp.get_precision('Purchase Price'), readonly=True, states={'draft': [('readonly', False)]}),
    }

    _defaults = {
        'with_bom': False,
    }

    def _get_mrp_bom_value(self, cr, uid, ids, bom_line, price_unit, sequence, context=None):

        line_bom = {
            'parent_id': False,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': bom_line.product_qty,
            'product_uom': bom_line.product_uom.id,
            'price_unit': price_unit,
            'price_subtotal': bom_line.product_qty * price_unit,
            'sequence': sequence,
        }
        if ids and len(ids) == 1:
            line_bom['order_id'] = ids[0]
        return line_bom
    
    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False,
                          packaging=False, fiscal_position=False, flag=False, context=None):

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product_id, qty, uom, qty_uos, uos, name, partner_id,
                                                                lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        context = context or self.pool['res.users'].context_get(cr, uid)
        # if not isinstance(ids, list):
        #     ids = [ids]
        if not context.get('calculate_bom', True):
            return result
        if product_id:
            uom_obj = self.pool['product.uom']
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            sequence = 0
            if product.bom_lines:
                result['value']['with_bom'] = True

                mrp_bom = product.bom_lines[0]
                # line_mrp_bom_obj = self.pool.get('sale.order.line.mrp.bom')
                mrp_bom_ids = [mrp_bom.id]
                if mrp_bom.bom_lines:
                    result['value']['mrp_bom'] = []
                    for bom_line in mrp_bom.bom_lines:
                        mrp_bom_ids.append(bom_line.id)
                        if bom_line.product_id.bom_lines:
                            for bom_sub_line in bom_line.product_id.bom_lines[0].bom_lines:
                                sequence += 1
                                price_unit = self.pool['product.uom']._compute_price(cr, uid,
                                                                                     bom_sub_line.product_id.uom_id.id,
                                                                                     bom_sub_line.product_id.cost_price,
                                                                                     bom_sub_line.product_uom.id)

                                line_bom = self._get_mrp_bom_value(cr, uid, ids, bom_sub_line, price_unit, sequence,
                                                                   context)
                                line_bom.update({
                                    'parent_id': bom_line.product_id.id,
                                    'product_uom_qty': line_bom['product_uom_qty'] * bom_line.product_qty,
                                    'price_subtotal': line_bom['price_subtotal'] * bom_line.product_qty,
                                })
                                result['value']['mrp_bom'].append(line_bom)
                                mrp_bom_ids.append(bom_sub_line.id)
                        else:
                            sequence += 1
                            price_unit = self.pool['product.uom']._compute_price(cr, uid, bom_line.product_id.uom_id.id,
                                                                                 bom_line.product_id.cost_price,
                                                                                 bom_line.product_uom.id)
                            line_bom = self._get_mrp_bom_value(cr, uid, ids, bom_line, price_unit, sequence, context)

                            result['value']['mrp_bom'].append(line_bom)
                price = 0
                if not context.get('exclude_routing', False):
                    routing_ids = []
                    for value in self.pool['mrp.bom']._get_ext_routing(cr, uid, mrp_bom_ids, '', '', context=context).values():
                        if value:
                            routing_ids.append(value)

                    workcenter_obj = self.pool['mrp.routing.workcenter']
                    workcenter_ids = workcenter_obj.search(cr, uid, [('routing_id', 'in', routing_ids)], context=context)
                    for wline in workcenter_obj.browse(cr, uid, workcenter_ids, context):
                        wc = wline.workcenter_id
                        cycle = wline.cycle_nbr
                        price += wc.costs_cycle * cycle + wc.costs_hour * wline.hour_nbr
                price /= mrp_bom.product_qty
                price = uom_obj._compute_price(cr, uid, mrp_bom.product_uom.id, price, mrp_bom.product_id.uom_id.id)
                result['value']['cost_price_unit_routing'] = price

            else:
                result['value'].update(
                    {'with_bom': False,
                     'mrp_bom': [],
                     })

        else:
            result['value'].update(
                {'with_bom': False,
                 'mrp_bom': [],
                 })
        # {'value': result, 'domain': domain, 'warning': warning}
        return result

    def onchange_mrp_bom(self, cr, uid, ids, product_id, mrp_bom, cost_price_unit_routing, context=None):

        if not mrp_bom:
            return {'value': {}}

        price = 0.
        no_change_line_id = []

        for line in mrp_bom:
            if line[2] and line[2].get('price_subtotal'):
                price += line[2].get('price_subtotal')
            else:
                line[1] and no_change_line_id.append(line[1])  # append only if line[1] have a value

        if no_change_line_id:
            for line_bom in self.pool['sale.order.line.mrp.bom'].browse(cr, uid, no_change_line_id, context):
                price += line_bom.price_subtotal

        res = {'purchase_price': price + cost_price_unit_routing}

                    # convert_to_price_uom = (lambda price: product_uom_obj._compute_price(
                    #     cr, uid, product.uom_id.id,
                    #     price, price_uom_id))
                    # if rule.price_surcharge:
                    #     price_surcharge = convert_to_price_uom(rule.price_surcharge)
                    #     price += price_surcharge
                    #
                    # if rule.price_min_margin:
                    #     price_min_margin = convert_to_price_uom(rule.price_min_margin)
                    #     price = max(price, price_limit + price_min_margin)
                    #
                    # if rule.price_max_margin:
                    #     price_max_margin = convert_to_price_uom(rule.price_max_margin)
                    #     price = min(price, price_limit + price_max_margin)

        return {'value': res}

