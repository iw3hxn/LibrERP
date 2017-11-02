# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Didotech SRL
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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
##############################################################################

from openerp.osv import orm, fields


class temp_mrp_bom(orm.TransientModel):
    _inherit = 'mrp.bom'
    _name = 'temp.mrp.bom'

    def _stock_availability(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        warehouse_order_point_obj = self.pool['stock.warehouse.orderpoint']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if not line.order_requirement_line_id:
                res[line.id] = {
                    'stock_availability': 0,
                    'spare': 0,
                }
                continue
            spare = 0
            warehouse = line.order_requirement_line_id.order_id.sale_order_id.shop_id.warehouse_id
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
        'order_requirement_line_id': fields.many2one('order.requirement.line', 'Order requirement line'),
        # 'child_complete_ids': fields.function(_child_compute, relation='temp.mrp.bom', string="BoM Hierarchy", type='many2many'),
        'bom_lines': fields.one2many('temp.mrp.bom', 'bom_id', 'BoM Lines'),
        'bom_id': fields.many2one('temp.mrp.bom', 'Parent BoM', ondelete='cascade', select=True),
        'product_type': fields.related('product_id', 'type', type='char', string='Product Type', readonly=True, store=False),
        'is_manufactured': fields.boolean('Manufacture'),
        'supplier_ids': fields.many2many('res.partner', string='Suppliers'),
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain="[('id', 'in', supplier_ids[0][2])]"),
        'stock_availability': fields.function(_stock_availability, method=True, multi='stock_availability',
                                              type='float', string='Stock Availability', readonly=True),
        'spare': fields.function(_stock_availability, method=True, multi='stock_availability', type='float',
                                 string='Spare', readonly=True),
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True),
    }

    _parent_name = 'bom_id'

    def _check_product(self, cr, uid, ids, context=None):
        # Serve per permettere l'inserimento di una BoM con lo stesso bom_id e product_id ma con position diversa.
        # La position è la descrizione.
        return True

    _constraints = [
        (_check_product, 'BoM line product should not be same as BoM product.', ['product_id']),
    ]

    def onchange_manufacture(self, cr, uid, ids, context=None):
        current_temp_mrp_bom = self.browse(cr, uid, ids, context)[0]
        if current_temp_mrp_bom.is_manufactured:
            # If yes write False and vice-versa
            self.write(cr, uid, ids[0], {'is_manufactured': False}, context)
        else:
            # If manufactured, no suppliers must be specified
            self.write(cr, uid, ids[0], {'is_manufactured': True, 'supplier_id': False}, context)

    ### TODO CALL THE ORDER_REQUIREMENT_LINE_SUPPLIERS.onchange_product_id
    def onchange_product_id(self, cr, uid, ids, product_id, qty=0, supplier_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        supplierinfo_obj = self.pool['product.supplierinfo']
        result_dict = {}
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context)
            if not supplier_id:
                # --find the supplier
                supplier_info_ids = supplierinfo_obj.search(cr, uid,
                                                            [('product_id', '=', product.product_tmpl_id.id)],
                                                            order="sequence", context=context)
                supplier_infos = supplierinfo_obj.browse(cr, uid, supplier_info_ids, context=context)
                seller_ids = [info.name.id for info in supplier_infos]

                if seller_ids:
                    result_dict.update({
                        'supplier_id': seller_ids[0],
                        'supplier_ids': seller_ids,
                    })
                else:
                    result_dict.update({
                        'supplier_id': False,
                        'supplier_ids': [],
                    })
        else:
            result_dict.update({
                'supplier_id': False,
                'supplier_ids': [],
            })
        return {'value': result_dict}
