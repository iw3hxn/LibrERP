# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-Today OpenERP SA (<http://www.openerp.com>).
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

import time
import netsvc
from osv import osv, fields

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    def generate_purchase_order(self, cr, uid, ids, supplier_id, pricelist_id, warehouse_id, context=None):
        purchase_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        warehouse_obj = self.pool.get('stock.warehouse')
        
        warehouse = warehouse_obj.browse(cr, uid, warehouse_id, context=context)
        if not warehouse:
            return False
        if isinstance(warehouse, list):
            warehouse = warehouse[0]
        
        for order in self.browse(cr, uid, ids, context=context):
            vals = {}
            vals = purchase_obj.onchange_partner_id(cr, uid, [], supplier_id)['value']
            vals['origin'] = order.name
            vals['partner_id'] = supplier_id
            vals['pricelist_id'] = pricelist_id
            vals['warehouse_id'] = warehouse_id
            vals['location_id'] = warehouse.lot_input_id.id
            vals['date_order'] = order.date_order
            purchase_id = purchase_obj.create(cr, uid, vals, context=context)
            
            for line in order.order_line:
                if not line.product_id:
                    continue
                    
                line_vals = purchase_line_obj.onchange_product_id(cr, uid, ids, pricelist_id, line.product_id.id,
                                                line.product_uom_qty, line.product_uom.id, supplier_id,
                                                date_order=order.date_order, context=context)['value']
                line_vals['name'] = line.name
                line_vals['product_id'] = line.product_id.id
                if not line_vals.get('price_unit', False):
                    line_vals['price_unit'] = line.price_unit
                line_vals['product_uom'] = line.product_uom.id
                line_vals['product_uom_qty'] = line.product_uom_qty
                line_vals['order_id'] = purchase_id
                purchase_line_obj.create(cr, uid, line_vals, context=context)
        
        return True

sale_order()

