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


class sale_order_line_mrp_bom(orm.Model):
    _name = 'sale.order.line.mrp.bom'
    _description = 'Sales Order Bom Line'
    
    _columns = {
        'name': fields.char('Note', size=256, select=True),
        'order_id': fields.many2one('sale.order.line', 'Order Reference', ondelete='cascade', select=True),
        'parent_id': fields.many2one('product.product', 'Parent', change_default=True),
        'product_id': fields.many2one('product.product', 'Product', change_default=True),
        'product_uom_qty': fields.float('Quantity (UoM)', digits_compute=dp.get_precision('Product UoS'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Purchase Price')),
        'price_subtotal': fields.float('Subtotal', required=True, digits_compute=dp.get_precision('Purchase Price')),
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
            # partner_id = context.get('partner_id', False)
            # self.pool['sale.order.line'].product_id_change(cr, uid, ids, 1, product_id, qty=product_qty, uom=uom_id, partner_id=partner_id, context=context)
            price_unit = price_unit or product.cost_price
            return {'value': {
                'price_unit': price_unit,
                'product_uom': uom_id or product.uom_id.id,
                'price_subtotal': price_unit * product_qty,
            }}
        else:
            return {'value': {}}
