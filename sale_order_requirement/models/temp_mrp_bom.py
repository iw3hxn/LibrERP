# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import decimal_precision as dp
from mrp import mrp_bom

default_row_colors = ['black', 'darkblue', 'cadetblue', 'grey']


class temp_mrp_bom(orm.Model):
    _name = 'temp.mrp.bom'

    # This is called also when loading saved temp mrp boms,
    # during creation see get_temp_mrp_bom
    def _stock_availability(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        order_requirement_line_obj = self.pool['order.requirement.line']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            product = line.product_id
            warehouse_id = line.sale_order_id.shop_id.warehouse_id.id
            ordreqline = order_requirement_line_obj.browse(cr, uid, line.order_requirement_line_id.id, context)
            res[line.id] = ordreqline.generic_stock_availability(product=product, warehouse_id=warehouse_id, context=context)
        return res

    # This is called also when loading saved temp mrp boms,
    # during creation see get_temp_mrp_bom
    def _get_routing(self, cr, uid, ids, field_name, arg, context):
        res = {}
        mrp_bom_obj = self.pool['mrp.bom']
        for line in self.browse(cr, uid, ids, context):
            product_id = line.product_id
            routing_id = mrp_bom_obj.search_browse(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], context)
            res[line.id] = routing_id
        return res

    def _is_belowspare(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = line.stock_availability < line.spare
        return res

    @staticmethod
    def get_color_bylevel(level):
        try:
            row_color = default_row_colors[level]
        except IndexError:
            row_color = 'grey'
        return row_color

    def get_color(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            row_color = temp_mrp_bom.get_color_bylevel(line.level)
            res[line.id] = row_color
        return res

    _columns = {
        'name': fields.char('Name', size=160, readonly=True),
        'level_name': fields.char('Level', readonly=True),
        'order_requirement_line_id': fields.many2one('order.requirement.line', 'Order requirement line', required=True,
                                                     ondelete='cascade'),
        'bom_id': fields.many2one('temp.mrp.bom', 'Parent BoM', select=True, ondelete='cascade'),
        'bom_lines': fields.one2many('temp.mrp.bom', 'bom_id', 'BoM Lines'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_qty': fields.float('Product Qty', required=True, digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True,
                                       help="UoM (Unit of Measure) is the unit of measurement for the inventory control"),
        'cost': fields.float('Cost', readonly=True),
        'product_type': fields.char('Pr.Type', size=10, readonly=True),
        'sale_order_id': fields.related('order_requirement_line_id', 'order_requirement_id', 'sale_order_id',
                                        string='Sale Order', relation='sale.order', type='many2one', readonly=True),
        'mrp_bom_id': fields.many2one('mrp.bom'),
        'mrp_bom_parent_id': fields.many2one('mrp.bom'),
        'mrp_routing_id': fields.many2one('mrp.routing', string='Routing', auto_join=True, readonly=True),
        'temp_mrp_routing_lines': fields.one2many('temp.mrp.routing', 'temp_mrp_bom_id', 'Routing Lines'),
        'mrp_production_id': fields.many2one('mrp.production', string='Manufacturing Order'),
        # TODO define well
        'purchase_order_line_id': fields.many2one('purchase.order.line', string='Purchase Order'),
        'level': fields.integer('Level'),
        'is_manufactured': fields.boolean('Manufacture'),
        'supplier_ids': fields.many2many('res.partner', string='Suppliers'),
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain="[('id', 'in', supplier_ids[0][2])]"),
        'stock_availability': fields.function(_stock_availability, method=True, multi='stock_availability',
                                              type='float', string='Stock Availability', readonly=True),
        'spare': fields.function(_stock_availability, method=True, multi='stock_availability', type='float',
                                 string='Spare', readonly=True),
        'is_belowspare': fields.function(_is_belowspare, method=True, type='boolean', string='', store=False),
        'desired_qty': fields.integer('Desired Qty'),
        'is_leaf': fields.boolean('Leaf', readonly=True),
        'position': fields.char('Internal Reference', size=64, help="Reference to a position in an external plan.",
                                readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True, store=False),
        'sequence': fields.integer('Sequence index')
    }

    _order = 'sequence,level'

    _defaults = {
        'level': 1  # Useful for insertion of new temp mrp boms
    }

    def _check_product(self, cr, uid, ids, context=None):
        # Serve per permettere l'inserimento di una BoM con lo stesso bom_id e product_id ma con position diversa.
        # La position è la descrizione.
        return True

    _constraints = [
        (_check_product, 'BoM line product should not be same as BoM product.', ['product_id']),
    ]

    # @staticmethod
    # def get_all_temp_bom_children_ids(father, temp_mrp_bom_ids):
    #     # Retrieve recursively all children
    #     # father is a dict of vals, temp_mrp_bom_ids must be in the form [ [x,x,{}], ... ]
    #     try:
    #         father_id = father['mrp_bom_id']
    #     except (KeyError, TypeError):
    #         return []
    #     children = [t for t in temp_mrp_bom_ids if
    #                 t[2] and 'mrp_bom_parent_id' in t[2] and t[2]['mrp_bom_parent_id'] == father_id]
    #     res = children
    #     for child in children:
    #         vals = child[2]
    #         res.extend(temp_mrp_bom.get_all_temp_bom_children_ids(vals['mrp_bom_id'], temp_mrp_bom_ids))
    #     return res

    @staticmethod
    def has_children(temp, vals):
        children_ids = [v for v in vals if v['bom_id'] == temp.id]
        return bool(children_ids)

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
        father_id = temp['bom_id']
        parents_ids = [t for t in temp_mrp_bom_ids if t[2] and 'id' in t[2] and t[2]['id'] == father_id]
        if level == 1:
            return bool(parents_ids)
        for parent in parents_ids:
            vals = parent[2]
            if temp_mrp_bom.check_parents(vals, temp_mrp_bom_ids):
                return True
        return False

    # TODO ALL onchange here USELESS
    # def onchange_temp_manufacture(self, cr, uid, ids, is_manufactured):
    #     res = {}
    #     if is_manufactured:
    #         res['supplier_id'] = False
    #     res['is_manufactured'] = is_manufactured
    #     return {'value': res}
    #
    # def onchange_temp_supplier_id(self, cr, uid, ids, supplier_id, product_id, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     res = {}
    #     return {'value': res}
    #
    def onchange_temp_product_id(self, cr, uid, ids, temp_id, father_temp_id, level, new_product_id, qty, context=None):
        if temp_id is not False:
            # TODO: For now use this ONLY WHEN CREATE NEW TEMP MRP BOM
            return
        context = context or self.pool['res.users'].context_get(cr, uid)
        context['create_flag'] = True
        order_requirement_line_obj = self.pool['order.requirement.line']

        line_id = context['line_id']
        line = order_requirement_line_obj.browse(cr, uid, line_id, context)

        # temp_ids, temp_routing = line.create_temp_mrp_bom(product_id=new_product_id, father_temp_id=father_temp_id,
        #                                                   start_level=level, create_father=True, context=context)

        ret = {}
        ret = line.get_temp_vals(product_id=new_product_id, father_temp_id=father_temp_id, level=level, context=context)
        # if temp_ids:
        #     ret = temp_ids[0]

        from pprint import pprint
        pprint(ret)
        return {'value': ret}
