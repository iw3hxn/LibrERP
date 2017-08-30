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


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    
    _columns = {
        'mrp_bom': fields.one2many('sale.order.line.mrp.bom', 'order_id', 'Bom Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'with_bom': fields.boolean(string='With BOM'),
    }
    
    _defaults = {
        'with_bom': False,
    }
    
    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False,
                          packaging=False, fiscal_position=False, flag=False, context=None):

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product_id, qty, uom, qty_uos, uos, name, partner_id,
                                                                lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        # if not isinstance(ids, list):
        #     ids = [ids]
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            sequence = 0
            if product.supply_method == 'produce':
                result['value']['with_bom'] = True
                if product.bom_lines:
                    mrp_bom = product.bom_lines[0]
                    # line_mrp_bom_obj = self.pool.get('sale.order.line.mrp.bom')
                    if mrp_bom.bom_lines:
                        result['value']['mrp_bom'] = []
                        for bom_line in mrp_bom.bom_lines:
                            if bom_line.product_id.bom_lines:
                                for bom_sub_line in bom_line.product_id.bom_lines[0].bom_lines:
                                    sequence += 1
                                    price_unit = self.pool['product.uom']._compute_price(cr, uid,
                                                                                         bom_sub_line.product_id.uom_id.id,
                                                                                         bom_sub_line.product_id.cost_price,
                                                                                         bom_sub_line.product_uom.id)
                                    line_bom = {
                                        'parent_id': bom_line.product_id.id,
                                        'product_id': bom_sub_line.product_id.id,
                                        'product_uom_qty': bom_sub_line.product_qty,
                                        'product_uom': bom_sub_line.product_uom.id,
                                        'price_unit': price_unit,
                                        'price_subtotal': bom_sub_line.product_qty * price_unit,
                                        'sequence': sequence,
                                    }
                                    if ids and len(ids) == 1:
                                        line_bom['order_id'] = ids[0]
                                    result['value']['mrp_bom'].append(line_bom)
                            else:
                                sequence += 1
                                price_unit = self.pool['product.uom']._compute_price(cr, uid, bom_line.product_id.uom_id.id, bom_line.product_id.cost_price, bom_line.product_uom.id)
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
                                result['value']['mrp_bom'].append(line_bom)
            else:
                result['value']['with_bom'] = False
            result['value']['with_bom'] = True
        # {'value': result, 'domain': domain, 'warning': warning}
        return result

    def onchange_mrp_bom(self, cr, uid, ids, mrp_bom, context=None):

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

        return {'value': {'purchase_price': price}}

