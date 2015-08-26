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

        mrp_bom_obj = self.pool['mrp.bom']
        
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            if product.supply_method == 'produce':
                result['value']['with_bom'] = True

                mrp_bom_ids = mrp_bom_obj.search(cr, uid, [('product_id', '=', product_id), ], context=context)
                if mrp_bom_ids and len(mrp_bom_ids) == 1:
                    mrp_bom = mrp_bom_obj.browse(cr, uid, mrp_bom_ids[0], context=context)
                    # line_mrp_bom_obj = self.pool.get('sale.order.line.mrp.bom')
                    if mrp_bom.bom_lines:
                        result['value']['mrp_bom'] = []
                        for bom_line in mrp_bom.bom_lines:
                            line_bom = {
                                'product_id': bom_line.product_id.id,
                                'product_uom_qty': bom_line.product_qty,
                                'product_uom': bom_line.product_uom.id,
                                'price_unit': bom_line.product_id.cost_price,
                                'price_subtotal': bom_line.product_qty * bom_line.product_id.cost_price
                            }
                            if ids and len(ids) == 1:
                                line_bom['order_id'] = ids[0]
                            result['value']['mrp_bom'].append(line_bom)
            else:
                result['value']['with_bom'] = False
        # {'value': result, 'domain': domain, 'warning': warning}
        return result

    def onchange_mrp_bom(self, cr, uid, ids, mrp_bom, context=None):

        price = 0.
        no_change_line_id = []

        for line in mrp_bom:
            if line[2] and line[2].get('price_subtotal'):
                price += line[2].get('price_subtotal')
            else:
                line[1] and no_change_line_id.append(line[1]) # append only if line[1] have a value

        if no_change_line_id:
            for line_bom in self.pool['sale.order.line.mrp.bom'].browse(cr, uid, no_change_line_id, context):
                price += line_bom.price_subtotal


        return {'value': {'purchase_price': price}}


class sale_order_line_mrp_bom(orm.Model):
    _name = 'sale.order.line.mrp.bom'
    _description = 'Sales Order Bom Line'
    
    _columns = {
        'name': fields.char('Note', size=256, select=True),
        'order_id': fields.many2one('sale.order.line', 'Order Reference', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', change_default=True),
        'product_uom_qty': fields.float('Quantity (UoM)', digits_compute=dp.get_precision('Product UoS'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Sale Price')),
        'price_subtotal': fields.float('Subtotal', required=True, digits_compute=dp.get_precision('Sale Price')),
    }
    
    _order = 'sequence, id'

    _defaults = {
        'product_uom_qty': 1,
        'sequence': 10,
        'price_unit': 0.0,
        'order_id': lambda self, cr, uid, context: context.get('default_sale_order_line', False) or False
    }

    def bom_product_id_change(self, cr, uid, ids, product_id, uom_id, product_qty, price_unit, context=None):
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            #qty = self.pool['product.uom']._compute_qty(cr, uid,
            #                           from_uom_id=uom_id,
            #                           qty=product_qty,
            #                           to_uom_id=uom_id)
            return {'value': {
                'price_unit': price_unit or product.cost_price,
                'product_uom': uom_id or product.uom_id.id,
                'price_subtotal': price_unit * product_qty,
            }}
        else:
            return {'value': {}}
