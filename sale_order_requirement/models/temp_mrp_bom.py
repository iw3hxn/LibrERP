# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

import tools

import decimal_precision as dp
from mrp import mrp_bom
from openerp.osv import orm, fields
from ..util import rounding

default_row_colors = ['black', 'darkblue', 'cadetblue', 'grey']


class temp_mrp_bom(orm.Model):
    _name = 'temp.mrp.bom'

    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = []
        if not ids:
            return res
        if isinstance(ids, (int, long)):
            ids = [ids]
        for bom_required in self.browse(cr, uid, ids, context=context):
            name = u"{}: {} {}".format(bom_required.sale_order_id.name, bom_required.product_qty, bom_required.product_uom.name)
            res.append((bom_required.id, name))
        return res

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

    def _is_out_of_stock(self, cr, uid, ids, name, args, context=None):
        # Return True if stock is less than spare
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.stock_availability < line.spare
        return res

    # This is called also when loading saved temp mrp boms,
    # during creation see get_temp_mrp_bom
    def _get_routing(self, cr, uid, ids, field_name, arg, context):
        res = {}
        mrp_bom_obj = self.pool['mrp.bom']
        for line in self.browse(cr, uid, ids, context):
            product_id = line.product_id
            routing_id = mrp_bom_obj.search_browse(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], context)
            # Here routing_id must be a browse record, not a list
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
        'type': fields.selection([('normal', 'Normal BoM'), ('phantom', 'Sets / Phantom')], 'BoM Type', required=True,
                                 help="If a sub-product is used in several products, it can be useful to create its own BoM. " \
                                      "Though if you don't want separated production orders for this sub-product, select Set/Phantom as BoM type. " \
                                      "If a Phantom BoM is used for a root product, it will be sold and shipped as a set of components, instead of being produced."),
        'level_name': fields.char('Level', readonly=True),
        'order_requirement_line_id': fields.many2one('order.requirement.line', 'Order requirement line', required=True,
                                                     ondelete='cascade'),
        'bom_id': fields.many2one('temp.mrp.bom', 'Parent BoM', select=True, ondelete='cascade'),
        'bom_lines': fields.one2many('temp.mrp.bom', 'bom_id', 'BoM Lines'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'original_qty': fields.float('Original Qty', required=True, digits_compute=dp.get_precision('Product UoM'), readonly=True),
        'product_qty': fields.float('Product Qty', required=True, digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'UOM', # Removed otherwise is impossible to add required=True,
                                       help="UoM (Unit of Measure) is the unit of measurement for the inventory control"),
        'product_uos': fields.many2one('product.uom', 'Product UOS',
                                       help="Product UOS (Unit of Sale) is the unit of measurement for the invoicing and promotion of stock."),
        'product_efficiency': fields.float('Manufacturing Efficiency', required=True,
                                           help="A factor of 0.9 means a loss of 10% within the production process."),
        'product_rounding': fields.float('Product Rounding', help="Rounding applied on the product quantity."),
        'type': fields.selection([('normal','Normal BoM'),('phantom','Sets / Phantom')], 'BoM Type', required=True,
                                 help= "If a sub-product is used in several products, it can be useful to create its own BoM. "\
                                 "Though if you don't want separated production orders for this sub-product, select Set/Phantom as BoM type. "\
                                 "If a Phantom BoM is used for a root product, it will be sold and shipped as a set of components, instead of being produced."),
        'partial_cost': fields.float('Partial Cost', readonly=True),
        'cost': fields.float('Cost', readonly=True),
        'product_type': fields.char('Pr.Type', size=10, readonly=True),
        'sale_order_id': fields.related('order_requirement_line_id', 'order_requirement_id', 'sale_order_id',
                                        string='Sale Order', relation='sale.order', type='many2one', readonly=True),
        # mrp_bom_id and mrp_bom_parent_id point to the original mrp bom
        'mrp_bom_id': fields.many2one('mrp.bom'),
        'mrp_bom_parent_id': fields.many2one('mrp.bom'),
        # mrp_routing_id is a relation with ORIGINAL routing (but we make a copy)
        'mrp_routing_id': fields.many2one('mrp.routing', string='Routing', auto_join=True, readonly=True),
        'temp_mrp_routing_lines': fields.one2many('temp.mrp.routing', 'temp_mrp_bom_id', 'Routing Lines'),
        'mrp_production_id': fields.many2one('mrp.production', string='Manufacturing Order'),
        # 'mrp_production_line_id': fields.many2one('mrp.production.???', string='Manufacturing Order'),
        'purchase_order_id': fields.many2one('purchase.order', string='Purchase Order'),
        'purchase_order_line_id': fields.many2one('purchase.order.line', string='Purchase Order Line'),
        'level': fields.integer('Level'),
        'is_manufactured': fields.boolean('Manufacture'),
        'buy': fields.boolean('Buy'),
        'supplier_ids': fields.many2many('res.partner', string='Suppliers', ondelete='cascade'),
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
        'sequence': fields.integer('Sequence index'),
        'is_out_of_stock': fields.function(_is_out_of_stock, method=True, type='boolean', string='Out of Stock', readonly=True)
    }

    _order = 'sequence,level,id'

    _defaults = {
        'is_manufactured': True,
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

    def onchange_temp_product_id(self, cr, uid, ids, temp_id, new_product_id, qty, is_manufactured, context=None):
        # if temp_id is not False:
        #     # Use this ONLY WHEN CREATE NEW TEMP MRP BOM
        #     return
        context = context or self.pool['res.users'].context_get(cr, uid)
        context['create_flag'] = True
        order_requirement_line_obj = self.pool['order.requirement.line']

        line_id = context['line_id']
        line = order_requirement_line_obj.browse(cr, uid, line_id, context)
        # When creating, Father is the main father, level is 1
        father_temp_id = line.temp_mrp_bom_ids[0].id
        # temp_ids, temp_routing = line.create_temp_mrp_bom(product_id=new_product_id, father_temp_id=father_temp_id,
        #                                                   start_level=1, start_sequence=9999, create_father=True,
        #                                                   context=context)
        # ret = {}
        # if temp_ids:
        #     ret = temp_ids

        # Only get values version
        ret = line.get_temp_vals(product_id=new_product_id, qty_mult=qty, father_temp_id=father_temp_id, level=1, context=context)
        ret.update({
            'product_qty': qty,
            'is_manufactured': is_manufactured
        })

        return {'value': ret}

    def onchange_temp_product_qty(self, cr, uid, ids, qty, context=None):
        if 'line_id' not in context:
            return
        line_id = context['line_id']
        line = self.browse(cr, uid, line_id, context)
        return {'value': {'qty': qty}}

    def out_of_stock_button(self, cr, uid, ids, context=None):
        # Useless, button just for show an icon
        return

    def _temp_mrp_bom_explode(self, cr, uid, bom_father, bom_factor, context):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product.
        @param factor: Factor of product UoM.
        @param properties: A List of properties Ids.
        @param addthis: If BoM found then True else False.
        @param level: Depth level to find BoM lines starts from 10.
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        # NOTE: MRP.BOM version will find only the first-level children. Not good for temp.mrp.bom
        # WARNING: PHANTOM KITS NOT MANAGED

        user = self.pool['res.users'].browse(cr, uid, uid, context)
        split_mrp_production = user.company_id.split_mrp_production

        result = []
        result2 = []

        def _explode_rec(father, factor):

            for bom in father.bom_lines:
                factor = factor / (bom.product_efficiency or 1.0)
                factor = rounding(factor, bom.product_rounding)
                if factor < bom.product_rounding:
                    factor = bom.product_rounding

                # When NOT splitting orders, add only leaves
                # Remove if condition for add all, and not only leaves
                if split_mrp_production or bom.is_leaf:
                    result.append(
                        {
                            'name': bom.product_id.name,
                            'product_id': bom.product_id.id,
                            'product_qty': bom.product_qty * factor,
                            'product_uom': bom.product_uom.id,
                            'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                            'product_uos': bom.product_uos and bom.product_uos.id or False,
                        })
                # When splitting orders, explode first level children ONLY, so NO RECURSION
                if not split_mrp_production:
                    _explode_rec(bom, bom_factor)

            # Routing lines directly referenced by temp mrp bom
            for wc_use in bom_father.temp_mrp_routing_lines:
                result2.append({
                    'name': wc_use.name,
                    'workcenter_id': wc_use.workcenter_id.id,
                    'sequence': wc_use.sequence,
                    'cycle': wc_use.cycle,
                    'hour': wc_use.hour
                })

        _explode_rec(bom_father, bom_factor)
        return result, result2

