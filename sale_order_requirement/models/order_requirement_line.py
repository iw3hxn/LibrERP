# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Didotech SRL
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

import datetime

import decimal_precision as dp
from openerp.osv import orm, fields

from tools.translate import _

class order_requirement_line(orm.Model):

    _name = 'order.requirement.line'

    _rec_name = 'product_id'

    def _stock_availability(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        warehouse_order_point_obj = self.pool['stock.warehouse.orderpoint']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            spare = 0
            warehouse = line.order_id.sale_order_id.shop_id.warehouse_id
            order_point_ids = warehouse_order_point_obj.search(cr, uid, [('product_id', '=', line.product_id.id), ('warehouse_id', '=', warehouse.id)], context=context, limit=1)
            if order_point_ids:
                spare = warehouse_order_point_obj.browse(cr, uid, order_point_ids, context)[0].product_min_qty

            res[line.id] = {
                'stock_availability': line.product_id and line.product_id.type != 'service' and line.product_id.qty_available or False,
                'spare': spare,
            }
        return res

    def get_color(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = 'black'
            if line.stock_availability < line.spare:
                res[line.id] = 'red'
        return res

    _columns = {
        'new_product_id': fields.many2one('product.product', 'Choosen Product', readonly=True,
                                          states={'draft': [('readonly', False)]}),
        'product_id': fields.many2one('product.product', 'Original Product', readonly=True, states={'draft': [('readonly', False)]}),
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoS'), states={'draft': [('readonly', False)]}),
        'stock_availability': fields.function(_stock_availability, method=True, multi='stock_availability', type='float', string='Stock Availability', readonly=True),
        'spare': fields.function(_stock_availability, method=True, multi='stock_availability', type='float', string='Spare', readonly=True),
        'order_id': fields.many2one('order.requirement', 'Order Reference', required=True, ondelete='cascade', select=True,
                                    readonly=True, states={'draft': [('readonly', False)]}),
        'sequence': fields.integer('Sequence',
                                   help="Gives the sequence order when displaying a list of sales order lines."),
        'state': fields.selection(
            [('cancel', 'Cancelled'), ('draft', 'Draft'), ('done', 'Done')], 'State', required=True, readonly=True,
        ),
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True),
        'purchase_order_line_ids': fields.many2many('purchase.order.line', string='Purchase Order lines'),
        # 'temp_mrp_bom_ids': fields.one2many('temp.mrp.bom', 'order_requirement_line_id', 'BOM'),
    }

    _defaults = {
        'state': 'draft',
        'sequence': 10,
    }
