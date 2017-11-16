# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import decimal_precision as dp
from mrp import mrp_bom


class temp_mrp_bom(orm.Model):
    _name = 'temp.mrp.bom'

    # TODO Duplicated, same as order_requirement_line
    def generic_stock_availability(self, cr, uid, product, warehouse_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        warehouse_order_point_obj = self.pool['stock.warehouse.orderpoint']
        spare = 0
        # product = self._get_actual_product(cr, uid, ids)
        order_point_ids = warehouse_order_point_obj.search(cr, uid, [('product_id', '=', product.id),
                                                                     ('warehouse_id', '=', warehouse_id)], context=context, limit=1)
        if order_point_ids:
            spare = warehouse_order_point_obj.browse(cr, uid, order_point_ids, context)[0].product_min_qty

        res = {
            'stock_availability': product.id and product.type != 'service' and product.qty_available or False,
            'spare': spare,
        }
        return res

    def _stock_availability(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            product = line.product_id
            warehouse_id = line.sale_order_id.shop_id.warehouse_id.id
            res[line.id] = self.generic_stock_availability(cr, uid, product, warehouse_id, context)
        return res

    # TODO: evaluate if keeping it
    def _stock_availabilityOLD(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        warehouse_order_point_obj = self.pool['stock.warehouse.orderpoint']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'stock_availability': 0,
                'spare': 0,
            }
            spare = 0
            try:
                warehouse = line.sale_order_id.shop_id.warehouse_id
                order_point_ids = warehouse_order_point_obj.search(cr, uid, [('product_id', '=', line.product_id.id), ('warehouse_id', '=', warehouse.id)], context=context, limit=1)
                if order_point_ids:
                    spare = warehouse_order_point_obj.browse(cr, uid, order_point_ids, context)[0].product_min_qty

                res[line.id] = {
                    'stock_availability': line.product_id and line.product_id.type != 'service' and line.product_id.qty_available or False,
                    'spare': spare,
                }
            except Exception as e:
                print e.message
        return res

    @staticmethod
    def _get_color_bylevel(level):
        colors = ['black', 'blue', 'cadetblue', 'grey']
        try:
            row_color = colors[level]
        except IndexError:
            row_color = 'grey'
        return row_color

    def get_color(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            row_color = temp_mrp_bom._get_color_bylevel(line.level)
            if line.stock_availability < line.spare:
                row_color = 'red'
            res[line.id] = row_color
        return res

    _columns = {
        'name': fields.char('Name', size=160, readonly=True),
        'level_name': fields.char('Level', readonly=True),
        'order_requirement_line_id': fields.many2one('order.requirement.line', 'Order requirement line', required=True),
        'bom_lines': fields.one2many('temp.mrp.bom', 'bom_id', 'BoM Lines'),
        'bom_id': fields.many2one('temp.mrp.bom', 'Parent BoM', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_uos_qty': fields.float('Product UOS Qty'),
        'product_uos': fields.many2one('product.uom', 'Product UOS',
                                       help="Product UOS (Unit of Sale) is the unit of measurement for the invoicing and promotion of stock."),
        'product_qty': fields.float('Product Qty', required=True, digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True,
                                       help="UoM (Unit of Measure) is the unit of measurement for the inventory control"),
        'cost': fields.float('Cost'),
        'product_type': fields.char('Pr.Type', size=10, readonly=True),
        'sale_order_id': fields.related('order_requirement_line_id', 'order_requirement_id', 'sale_order_id',
                                        string='Sale Order', relation='sale.order', type='many2one', readonly=True),
        'tmp_id': fields.integer('tmp_id'),
        'tmp_parent_id': fields.integer('tmp_parent'),
        'parent_id': fields.many2one('temp.mrp.bom', 'Parent'),
        'level': fields.integer('Level'),
        # todo remove parent_id_num
        'parent_id_num': fields.related('parent_id', 'id', type='integer', string='Parent'),
        'is_manufactured': fields.boolean('Manufacture'),
        'supplier_ids': fields.many2many('res.partner', string='Suppliers'),
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain="[('id', 'in', supplier_ids[0][2])]"),
        'stock_availability': fields.function(_stock_availability, method=True, multi='stock_availability',
                                              type='float', string='Stock Availability', readonly=True),
        'spare': fields.function(_stock_availability, method=True, multi='stock_availability', type='float',
                                 string='Spare', readonly=True),
        'is_leaf': fields.boolean('Leaf', readonly=True),
        'position': fields.char('Internal Reference', size=64, help="Reference to a position in an external plan.",
                                readonly=True),

        'routing_id': fields.many2one('mrp.routing', 'Routing',
                                      help="The list of operations (list of work centers) to produce the finished product. The routing is mainly used to compute work center costs during operations and to plan future loads on work centers based on production planning."),
        'company_id': fields.many2one('res.company', 'Company', required=True),

        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True),
    }

    def _check_product(self, cr, uid, ids, context=None):
        # Serve per permettere l'inserimento di una BoM con lo stesso bom_id e product_id ma con position diversa.
        # La position è la descrizione.
        return True

    _constraints = [
        (_check_product, 'BoM line product should not be same as BoM product.', ['product_id']),
    ]

    @staticmethod
    def get_all_temp_bom_children_ids(father, temp_mrp_bom_ids):
        # Retrieve recursively all children
        # father is a dict of vals, temp_mrp_bom_ids must be in the form [ [x,x,{}], ... ]
        try:
            father_id = father['tmp_id']
        except (KeyError, TypeError):
            return []
        children = [t for t in temp_mrp_bom_ids if
                    t[2] and 'tmp_parent_id' in t[2] and t[2]['tmp_parent_id'] == father_id]
        res = children
        for child in children:
            vals = child[2]
            res.extend(temp_mrp_bom.get_all_temp_bom_children_ids(vals['tmp_id'], temp_mrp_bom_ids))
        return res

    @staticmethod
    def check_parents(temp, temp_mrp_bom_ids):
        # Return True if all the parents are present up to level 0
        # temp is a dict of vals, temp_mrp_bom_ids must be in the form [ [x,x,{}], ... ]
        try:
            level = temp['level']
        except (KeyError, TypeError):
            return False
        # If I am at level 0 => True (no need for lookup parents)
        if level == 0:
            return True
        # Direct fathers
        father_id = temp['tmp_parent_id']
        parents_ids = [t for t in temp_mrp_bom_ids if t[2] and 'tmp_id' in t[2] and t[2]['tmp_id'] == father_id]
        if level == 1:
            return bool(parents_ids)
        for parent in parents_ids:
            vals = parent[2]
            if temp_mrp_bom.check_parents(vals, temp_mrp_bom_ids):
                return True
        return False

    def onchange_temp_manufacture(self, cr, uid, ids, is_manufactured, context=None):
        res = {}
        if is_manufactured:
            res['supplier_id'] = False
        return {'value': res}

    def onchange_temp_supplier_id(self, cr, uid, ids, supplier_id, product_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        return {'value': res}

    def update_temp_mrp_data000(self, cr, uid, temp, context):
        # TODO DUPLICATED -> move into order_requirement_line and use in creation?
        context = context or self.pool['res.users'].context_get(cr, uid)
        product_obj = self.pool['product.product']
        order_requirement_line_obj = self.pool['order.requirement.line']

        line_id = temp['order_requirement_line_id']
        product_id = temp['product_id']
        level = temp['level']
        qty = temp['product_qty']
        line = order_requirement_line_obj.browse(cr, uid, line_id, context)
        product = product_obj.browse(cr, uid, product_id, context)

        row_color = temp_mrp_bom._get_color_bylevel(level)
        level_name = '- {} {} >'.format(str(level), ' -----' * level)

        suppliers = line.get_suppliers(product_id, qty, context=context)
        warehouse_id = line.sale_order_id.shop_id.warehouse_id.id
        stock_spare = self.generic_stock_availability(cr, uid, product, warehouse_id, context)
        if level > 0 and stock_spare['stock_availability'] < stock_spare['spare']:
            row_color = 'red'
        return {
            'row_color': row_color,
            'level_name': level_name,
            'stock_availability': stock_spare['stock_availability'],
            'spare': stock_spare['spare'],
            'supplier_id': suppliers['supplier_id'],
            'supplier_ids': suppliers['supplier_ids'],
        }

    def onchange_temp_product_id(self, cr, uid, ids, level, new_product_id, qty=0, context=None):
        order_requirement_line_obj = self.pool['order.requirement.line']
        line_id = context['line_id']
        line = order_requirement_line_obj.browse(cr, uid, line_id, context)
        temp = {
            'level': level,
            'product_id': new_product_id,
            'product_qty': qty,
            'order_requirement_line_id': line_id
        }
        ret = line.update_temp_mrp_data(cr, uid, temp=temp, context=context)
        return {'value': ret}

