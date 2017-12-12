# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

import tools
from tools.translate import _

import decimal_precision as dp
from openerp.osv import orm, fields
from temp_mrp_bom import temp_mrp_bom
from ..util import rounding

routing_colors = ['darkblue', 'forestgreen', 'orange', 'blue', 'grey']
sequence = 0

class order_requirement_line(orm.Model):

    _name = 'order.requirement.line'
    _rec_name = 'product_id'

    col = 0

    # def _get_actual_product(self, cr, uid, ids, name = None, args = None, context=None):
    #     line = self.browse(cr, uid, ids, context)[0]
    #     if line.new_product_id:
    #         return line.new_product_id
    #     else:
    #         return line.product_id

    def generic_stock_availability(self, cr, uid, ids, product, warehouse_id, context=None):
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
            if line.new_product_id:
                product = line.new_product_id
            else:
                product = line.product_id
            warehouse_id = line.sale_order_id.shop_id.warehouse_id.id
            res[line.id] = self.generic_stock_availability(cr, uid, [], product, warehouse_id, context)
        return res

    def get_color(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = 'black'
            if line.stock_availability < line.spare:
                res[line.id] = 'red'
            elif line.state == 'done':
                res[line.id] = 'green'
            elif line.temp_mrp_bom_ids:
                res[line.id] = 'cadetblue'
        return res

    def get_suppliers(self, cr, uid, ids, new_product_id, context=None):
        # Return FORMATTED supplier_ids [(6, False, [ID])] and a choosen supplier_id
        context = context or self.pool['res.users'].context_get(cr, uid)
        supplierinfo_obj = self.pool['product.supplierinfo']
        result_dict = {}
        if new_product_id:
            product = self.pool['product.product'].browse(cr, uid, new_product_id, context)
            # --find the supplier
            supplier_info_ids = supplierinfo_obj.search(cr, uid, [('product_id', '=', product.product_tmpl_id.id)],
                                                        order="sequence", context=context)
            supplier_infos = supplierinfo_obj.browse(cr, uid, supplier_info_ids, context=context)
            seller_ids = list(set([info.name.id for info in supplier_infos]))

            if seller_ids:
                supplier_id = seller_ids[0]
            else:
                supplier_id = False
                # If not suppliers found -> returns all of them
                supplier_info_ids = supplierinfo_obj.search(cr, uid,[], order="sequence", context=context)
                supplier_infos = supplierinfo_obj.browse(cr, uid, supplier_info_ids, context=context)
                seller_ids = list(set([info.name.id for info in supplier_infos]))

        else:
            supplier_id = False
            seller_ids = []

        result_dict.update({
            'supplier_id': supplier_id,
            'supplier_ids': [(6, False, [s for s in seller_ids])],
        })

        return result_dict

    def get_routing_id(self, cr, uid, product_id, context):
        mrp_bom_obj = self.pool['mrp.bom']
        mrp_bom_related = mrp_bom_obj.search_browse(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], context=context)
        if isinstance(mrp_bom_related, list):
            if len(mrp_bom_related) == 1:
                return mrp_bom_related[0].routing_id.id
            else:
                return False
        else:
            return mrp_bom_related.routing_id.id

    def get_routing_lines(self, cr, uid, ids, bom, temp_id, color, context=None):
        mrp_routing_workcenter_obj = self.pool['mrp.routing.workcenter']

        routing_id = self.get_routing_id(cr, uid, bom.product_id.id, context)
        workcenter_lines = mrp_routing_workcenter_obj.search_browse(cr, uid, [('routing_id', '=', routing_id)], context)
        ret_vals = []

        if not isinstance(workcenter_lines, list):
            workcenter_lines = [workcenter_lines]

        # From mrp._bom_explode
        factor = 1
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        if workcenter_lines:
            for wcl in workcenter_lines:
                wc = wcl.workcenter_id
                if wc.user_ids:
                    user_id = wc.user_ids[0].id
                else:
                    user_id = False

                # Prepare for writing
                user_ids = [(6, False, [u.id for u in wc.user_ids])]

                d, m = divmod(factor, wcl.workcenter_id.capacity_per_cycle)
                mult = (d + (m and 1.0 or 0.0))
                cycle = mult * wcl.cycle_nbr
                routing_vals = {
                    'mrp_routing_id': routing_id,
                    'name': tools.ustr(wcl.name) + ' - ' + tools.ustr(bom.product_id.name),
                    'workcenter_id': wc.id,
                    'sequence': wcl.sequence,
                    'cycle': cycle,
                    'hour': float(wcl.hour_nbr * mult + (
                        (wc.time_start or 0.0) + (wc.time_stop or 0.0) + cycle * (wc.time_cycle or 0.0)) * (
                                      wc.time_efficiency or 1.0)),
                    'row_color': color,
                    'temp_mrp_bom_id': temp_id,
                    'order_requirement_line_id': ids[0],
                    'user_ids': user_ids,
                    'user_id': user_id,
                }
                ret_vals.append(routing_vals)
        return ret_vals

    def _get_temp_vals_from_mrp_bom(self, cr, uid, ids, bom, temp_father_id, level, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        product_obj = self.pool['product.product']

        # Set temp values by original BOM
        line_id = ids[0]
        is_leaf = not bool(bom.child_buy_and_produce_ids)
        is_manufactured = not is_leaf

        product_id = bom.product_id.id

        line = self.browse(cr, uid, line_id, context)
        product = product_obj.browse(cr, uid, product_id, context)

        row_color = temp_mrp_bom.get_color_bylevel(level)
        level_name = '- {} {} >'.format(str(level), ' -----' * level)

        suppliers = line.get_suppliers(product_id, context=context)
        warehouse_id = line.sale_order_id.shop_id.warehouse_id.id
        stock_spare = self.generic_stock_availability(cr, uid, [], product, warehouse_id, context)
        routing_id = self.get_routing_id(cr, uid, product_id, context)

        return {
            'name': bom.name,
            'bom_id': temp_father_id,
            # mrp_bom_parent_id was very useful for reconstructing hierarchy
            'mrp_bom_id': bom.id,
            'type': bom.type,
            # 'mrp_bom_parent_id': bom_parent_id,
            'product_id': product_id,
            'original_qty': bom.product_qty,
            'product_qty': bom.product_qty,
            'product_uom': bom.product_uom.id,
            'product_uos': bom.product_uos.id,
            'product_efficiency': bom.product_efficiency,
            'product_rounding': bom.product_rounding,
            'product_type': bom.product_id.type,
            # TODO: VERSION STANDARD_PRICE
            'partial_cost': bom.product_id.standard_price,
            'cost': 0,
            'is_manufactured': is_manufactured,
            'company_id': bom.company_id.id,
            'position': bom.position,
            'is_leaf': is_leaf,
            'level': level,
            'order_requirement_line_id': line_id,
            'row_color': row_color,
            'level_name': level_name,
            'stock_availability': stock_spare['stock_availability'],
            'spare': stock_spare['spare'],
            'supplier_id': suppliers['supplier_id'],
            'supplier_ids': suppliers['supplier_ids'],
            'mrp_routing_id': routing_id
        }

    def _get_temp_vals_from_product(self, cr, uid, ids, product, temp_father_id, level, context):
        # Set temp values by product => LEAF
        context = context or self.pool['res.users'].context_get(cr, uid)
        product_obj = self.pool['product.product']

        line_id = ids[0]

        is_leaf = True
        is_manufactured = False

        product_id = product.id
        line = self.browse(cr, uid, line_id, context)
        product = product_obj.browse(cr, uid, product_id, context)

        row_color = temp_mrp_bom.get_color_bylevel(level)
        level_name = '- {} {} >'.format(str(level), ' -----' * level)

        suppliers = line.get_suppliers(product_id, context=context)
        warehouse_id = line.sale_order_id.shop_id.warehouse_id.id
        stock_spare = self.generic_stock_availability(cr, uid, [], product, warehouse_id, context)
        routing_id = self.get_routing_id(cr, uid, product_id, context)

        return {
            'name': product.name,
            'bom_id': temp_father_id,
            # Nonsense with a product
            'type': 'normal',
            # mrp_bom_parent_id was very useful for reconstructing hierarchy
            'mrp_bom_id': False,
            'mrp_bom_parent_id': False,
            'product_id': product_id,
            'original_qty': 1,
            'product_qty': 1,
            'product_uom': product.uom_id.id,
            # fixed to 0 with a product
            'product_efficiency': 0,
            'product_type': product.type,
            # TODO: VERSION STANDARD_PRICE
            'partial_cost': product.standard_price,
            'cost': 0,
            'company_id': product.company_id.id,
            # 'position': product.position,
            'level': level,
            'is_leaf': is_leaf,
            'is_manufactured': is_manufactured,
            'order_requirement_line_id': line_id,
            'row_color': row_color,
            'level_name': level_name,
            'stock_availability': stock_spare['stock_availability'],
            'spare': stock_spare['spare'],
            'supplier_id': suppliers['supplier_id'],
            'supplier_ids': suppliers['supplier_ids'],
            'mrp_routing_id': routing_id
        }

    def get_temp_vals(self, cr, uid, ids, product_id, father_temp_id, level, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        product_obj = self.pool['product.product']
        mrp_bom_obj = self.pool['mrp.bom']

        product = product_obj.browse(cr, uid, product_id, context)
        bom_ids = mrp_bom_obj.search_browse(cr, uid, [('product_id', '=', product_id),
                                                      ('bom_id', '=', False)], context=context)

        if bom_ids:
            # Get by its BOM
            if not isinstance(bom_ids, list):
                bom_ids = [bom_ids]
            return self._get_temp_vals_from_mrp_bom(cr, uid, ids, bom_ids[0], father_temp_id, level, context)
        else:
            # Get by products
            return self._get_temp_vals_from_product(cr, uid, ids, product, father_temp_id, level, context)

    def _sort_temp_mrp_bom(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        # Must be one line
        line = self.browse(cr, uid, ids, context)[0]
        temp_mrp_bom_ids = line.temp_mrp_bom_ids
        if not temp_mrp_bom_ids:
            return
        global sequence
        sequence = 0

        def _sort_rec(temp, temp_list):
            global sequence
            # Set sequence and do the same with children
            temp_mrp_bom_obj.write(cr, uid, temp.id, {'sequence': sequence}, context)
            sequence += 1
            direct_children = [c for c in temp_list if c.bom_id.id == temp.id]
            for t in direct_children:
                _sort_rec(t, temp_list)

        # Pass the first, recursion will do the rest
        _sort_rec(temp_mrp_bom_ids[0], temp_mrp_bom_ids)

    @staticmethod
    def _compute_cost(temp, temp_mrp_boms):
        # Simple version -> sum of partial_cost
        # COST: Cost of product itself + cost of all children
        cost = temp.partial_cost #* temp.product_qty #TODO VERIFY

        # Children
        for t in temp_mrp_boms:
            if t.bom_id.id == temp.id:
                cost += order_requirement_line._compute_cost(t, temp_mrp_boms)
        temp.cost = cost
        return cost

    def _update_cost(self, cr, uid, line_id, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        line = self.browse(cr, uid, line_id, context)
        if not line.temp_mrp_bom_ids:
            return
        temp = line.temp_mrp_bom_ids[0]
        temp_mrp_boms = line.temp_mrp_bom_ids

        order_requirement_line._compute_cost(temp, temp_mrp_boms)
        for t in temp_mrp_boms:
            temp_mrp_bom_obj.write(cr, uid, t.id, {'cost': t.cost}, context)

    def create_temp_mrp_bom(self, cr, uid, ids, product_id, father_temp_id, start_level, start_sequence=0,
                            create_father=True, create_children=True, context=None):
        # Returns 2 list of VALS (probably not needed)
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        temp_mrp_routing_obj = self.pool['temp.mrp.routing']
        product_obj = self.pool['product.product']
        mrp_bom_obj = self.pool['mrp.bom']

        temp_mrp_bom_vals = []
        temp_mrp_routing_vals = []
        global sequence
        sequence = start_sequence

        product = product_obj.browse(cr, uid, product_id, context)
        # bom_ids = product.bom_ids # NO, wrong, duplicates !
        bom_ids = mrp_bom_obj.search_browse(cr, uid, [('product_id', '=', product_id),
                                                      ('bom_id', '=', False)], context=context)

        def _get_rec(bom_rec, father_id, level):
            global sequence

            bom_children = bom_rec.child_buy_and_produce_ids
            if not bom_children:
                return
            for bom in bom_children:
                if bom.product_id.type == 'product':
                    temp_vals = self._get_temp_vals_from_mrp_bom(cr, uid, ids, bom, father_id, level, context)
                    temp_vals['sequence'] = sequence
                    sequence += 1
                    temp_id = temp_mrp_bom_obj.create(cr, uid, temp_vals, context)
                    temp_vals['id'] = temp_id
                    temp_mrp_bom_vals.append(temp_vals)
                    if temp_vals['mrp_routing_id']:
                        temp_routing_vals = self.get_routing_lines(cr, uid, ids, bom, temp_id, routing_colors[self.col], context)
                        temp_mrp_routing_vals.extend(temp_routing_vals)
                        self.col = (self.col+1) % len(routing_colors)

                    _get_rec(bom, temp_id, level + 1)
                # elif bom.product_id.type == 'service'
                # TODO => ? Create routing when product type = service

        if not bom_ids:
            # It's a product with no BoM
            temp_vals = self._get_temp_vals_from_product(cr, uid, ids, product, father_temp_id, start_level, context)
            temp_vals['sequence'] = sequence
            sequence += 1
            temp_id = temp_mrp_bom_obj.create(cr, uid, temp_vals, context)
            temp_vals['id'] = temp_id
            temp_mrp_bom_vals.append(temp_vals)
            # Calculate routing for Father Bom(s)
            # TODO ROUTING FROM PRODUCT ? EX.: I buy a product and I want to paint it
            # temp_mrp_routing_vals.extend(self.get_routing_lines(cr, uid, ids, bom, temp_id, 'black', context))
            return temp_mrp_bom_vals, temp_mrp_routing_vals

        if not isinstance(bom_ids, list):
            bom_ids = [bom_ids]

        for bom_father in bom_ids:
            # Main BOMs only if create_father = True
            if create_father:
                temp_vals = self._get_temp_vals_from_mrp_bom(cr, uid, ids, bom_father, father_temp_id, start_level, context)
                temp_vals['sequence'] = sequence
                sequence += 1
                temp_id = temp_mrp_bom_obj.create(cr, uid, temp_vals, context)
                temp_vals['id'] = temp_id
                temp_mrp_bom_vals.append(temp_vals)
                # Calculate routing for Father Bom(s)
                temp_mrp_routing_vals.extend(self.get_routing_lines(cr, uid, ids, bom_father, temp_id, 'black', context))
                if create_children:
                    _get_rec(bom_father, temp_id, start_level + 1)
            else:
                if create_children:
                    _get_rec(bom_father, father_temp_id, start_level + 1)

            for routing_vals in temp_mrp_routing_vals:
                temp_mrp_routing_obj.create(cr, uid, routing_vals, context)

        if not temp_mrp_bom_vals:
            raise orm.except_orm(_(u'Error !'),
                                 _(u'Not created, product error: {0}'.format(product.name)))

        self._update_cost(cr, uid, ids[0], context)

        # TODO vals not updated
        return temp_mrp_bom_vals, temp_mrp_routing_vals

    def _get_or_create_temp_bom(self, cr, uid, ids, name, args, context=None):
        # TODO: CAN BE REMOVED?
        context = context or self.pool['res.users'].context_get(cr, uid)
        view_bom = 'view_bom' in context and context['view_bom']

        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = {
                'temp_mrp_bom_ids': False,
                'temp_mrp_bom_routing_ids': False,
            }
            if not view_bom:
                continue
            if line.temp_mrp_bom_ids:
                res[line.id]['temp_mrp_bom_ids'] = [t.id for t in line.temp_mrp_bom_ids]
                res[line.id]['temp_mrp_bom_routing_ids'] = [t.id for t in line.temp_mrp_bom_routing_ids]
            else:
                # does not work here
                # product = line.actual_product
                if line.new_product_id:
                    product = line.new_product_id
                elif line.product_id:
                    product = line.product_id
                self.create_temp_mrp_bom(cr, uid, ids, product.id, False, 0, 0, True, True, context)
                # res[line.id]['temp_mrp_bom_ids'] = temp_mrp_bom_vals
                # res[line.id]['temp_mrp_bom_routing_ids'] = temp_mrp_routing_vals
                line_reload = self.browse(cr, uid, line.id, context)
                res[line.id]['temp_mrp_bom_ids'] = [t.id for t in line_reload.temp_mrp_bom_ids]
                res[line.id]['temp_mrp_bom_routing_ids'] = [t.id for t in line_reload.temp_mrp_routing_ids]

        return res

    _columns = {
        'new_product_id': fields.many2one('product.product', 'Choosen Product', readonly=True,
                                          states={'draft': [('readonly', False)]}),
        'product_id': fields.many2one('product.product', 'Original Product', readonly=True),
        # todo remove 'actual_product': fields.function(_get_actual_product, store=False),
        'is_manufactured': fields.boolean('Manufacture', readonly=True, states={'draft': [('readonly', False)]},
                                          help='If checked product is manufactured. If not, BOM is read-only'),
        'supplier_ids': fields.many2many('res.partner', string='Suppliers', readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain="[('id', 'in', supplier_ids[0][2])]",
                                       readonly=True, states={'draft': [('readonly', False)]}),
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoS'), readonly=True,
                            states={'draft': [('readonly', False)]}),
        'stock_availability': fields.function(_stock_availability, method=True, multi='stock_availability',
                                              type='float', string='Stock Availability', readonly=True),
        'spare': fields.function(_stock_availability, method=True, multi='stock_availability', type='float',
                                 string='Spare', readonly=True),
        'order_requirement_id': fields.many2one('order.requirement', 'Order Reference', required=True,
                                                ondelete='cascade', select=True),
        'sale_order_id': fields.related('order_requirement_id', 'sale_order_id', string='Sale Order',
                                        relation='sale.order', type='many2one', readonly=True),
        'sequence': fields.integer('Sequence',
                                   help="Gives the sequence order when displaying a list of sales order lines."),
        'state': fields.selection(
            [('cancel', 'Cancelled'), ('draft', 'Draft'), ('done', 'Done')], 'State', required=True, readonly=True,
        ),
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True),
        'purchase_order_ids': fields.many2many('purchase.order', string='Purchase Orders'),
        'purchase_order_line_ids': fields.many2many('purchase.order.line', string='Purchase Order lines'),
        'mrp_production_ids': fields.many2many('mrp.production', string='Production Orders'),
        'temp_mrp_bom_ids': fields.one2many('temp.mrp.bom', 'order_requirement_line_id', 'BoM Hierarchy'),
        'temp_mrp_bom_routing_ids': fields.one2many('temp.mrp.routing', 'order_requirement_line_id', 'BoM Routing'),
    }

    _defaults = {
        'state': 'draft',
        'sequence': 10,
    }

    # def fields_get(self, cr, uid, allfields=None, context=None):
    #     # Trying to show bom only if the button is pressed, not the click on the line
    #     # BUT the attrs invisible condition in xml overwrite it
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     ret = super(order_requirement_line, self).fields_get(cr, uid, allfields=allfields, context=context)
    #     view_bom = 'view_bom' in context and context['view_bom']
    #     ret['temp_mrp_bom_ids']['invisible'] = not view_bom
    #     ret['temp_mrp_bom_routing_ids']['invisible'] = not view_bom
    #     return ret

    def onchange_is_manufactured(self, cr, uid, ids, is_manufactured, new_product_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        result_dict = {}
        new_is_manufactured = is_manufactured
        # ONE LINE
        line = self.browse(cr, uid, ids, context)[0]
        if is_manufactured:
            if not line.temp_mrp_bom_ids:
                temp_mrp_bom_ids, temp_mrp_bom_routing_ids = self.create_temp_mrp_bom(cr, uid, ids, new_product_id, False, 0, 0,
                                                                      True, True, context)
                temp = temp_mrp_bom_ids[0]
                # TODO: maybe in create_temp
                if temp['is_leaf']:
                    # I don't want to see an "empty" bom with the father only
                    temp_mrp_bom_obj.unlink(cr, uid, temp['id'], context)
                    # Uncheck is_manufacture -> no Bom, no manufacture
                    new_is_manufactured = False
        else:
            if line.temp_mrp_bom_ids:
                father_temp_id = line.temp_mrp_bom_ids[0].id
                temp_mrp_bom_obj.unlink(cr, uid, father_temp_id, context)

        self.write(cr, uid, line.id, {'is_manufactured': new_is_manufactured})

        # RELOAD
        line = self.browse(cr, uid, ids, context)[0]
        temp_mrp_bom_ids = [t.id for t in line.temp_mrp_bom_ids]
        temp_mrp_bom_routing_ids = [t.id for t in line.temp_mrp_bom_routing_ids]

        result_dict.update({
            'temp_mrp_bom_ids': temp_mrp_bom_ids,
            'temp_mrp_bom_routing_ids': temp_mrp_bom_routing_ids,
            'is_manufactured': new_is_manufactured
        })

        return {'value': result_dict}

    def onchange_product_id(self, cr, uid, ids, new_product_id, qty=0, supplier_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result_dict = self.get_suppliers(cr, uid, ids, new_product_id, context)

        if new_product_id:
            temp_mrp_bom_obj = self.pool['temp.mrp.bom']
            product = self.pool['product.product'].browse(cr, uid, new_product_id, context)

            # Update BOM according to new product
            # Removing existing temp mrp bom
            line = self.browse(cr, uid, ids, context)[0]  # MUST BE ONE LINE
            if line.temp_mrp_bom_ids:
                temp_mrp_bom_ids = [temp['id'] for temp in line.temp_mrp_bom_ids]
                temp_mrp_bom_obj.unlink(cr, uid, temp_mrp_bom_ids, context)

            supplier_ids_formatted = result_dict['supplier_ids']
            self.write(cr, uid, line.id, {'new_product_id': product.id, 'supplier_ids': supplier_ids_formatted}, context)
            temp_ids, temp_routing_ids = self.create_temp_mrp_bom(cr, uid, ids, product.id, False, 0, 0, True, True, context)
            # TODO: maybe another option create_if_leaf in create_temp_mrp_bom
            temp = temp_ids[0]
            if temp['is_leaf']:
                # I don't want to see an "empty" bom with the father only
                temp_mrp_bom_obj.unlink(cr, uid, temp['id'], context)
                # Uncheck is_manufacture -> no Bom, no manufacture
                result_dict['is_manufactured'] = False
                self.write(cr, uid, line.id, {'is_manufactured': False})
        else:
            result_dict['view_bom'] = False

        # RELOAD
        line = self.browse(cr, uid, ids, context)[0]  # MUST BE ONE LINE
        temp_mrp_bom_ids = [t.id for t in line.temp_mrp_bom_ids]
        temp_mrp_bom_routing_ids = [t.id for t in line.temp_mrp_bom_routing_ids]

        result_dict.update({
            'temp_mrp_bom_ids': temp_mrp_bom_ids,
            'temp_mrp_bom_routing_ids': temp_mrp_bom_routing_ids,
            'view_bom': True
        })

        return {'value': result_dict}

    def onchange_qty(self, cr, uid, ids, qty, context=None):
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        line_id = ids[0]
        line = self.browse(cr, uid, line_id, context)
        for temp in line.temp_mrp_bom_ids:
            oldqty = temp.product_qty
            temp_mrp_bom_obj.write(cr, uid, temp.id, {'product_qty': oldqty * qty}, context)
        self._update_cost(cr, uid, line_id, context)
        return {'value': {'qty': qty}}

    def _get_temp_routing(self, bom):
        # Retrieve routing
        routing_vals = []
        for temp_routing in bom.temp_mrp_routing_lines:
            routing_vals.append({
                'name': temp_routing.name,
                'sequence': temp_routing.sequence,
                'workcenter_id': temp_routing.workcenter_id.id,
                'cycle': temp_routing.cycle,
                'hour': temp_routing.hour,
                'state': 'draft',
                'product_id': bom.product_id.id,
                'product_uom': bom.product_uom.id
            })
        return routing_vals

    def NO_NO_NO_make_production_internal_shipment(self, cr, uid, production, context=None):
        ir_sequence = self.pool.get('ir.sequence')
        stock_picking = self.pool.get('stock.picking')
        pick_type = 'internal'
        address_id = False

        # TODO: ASK, if I can change routing -> NOT THIS ROUTING but temp_mrp_routing_id
        # Take routing address as a Shipment Address.
        # If usage of routing location is a internal, make outgoing shipment otherwise internal shipment
        if production.bom_id.routing_id and production.bom_id.routing_id.location_id:
            routing_loc = production.bom_id.routing_id.location_id
            if routing_loc.usage != 'internal':
                pick_type = 'out'
            address_id = routing_loc.address_id and routing_loc.address_id.id or False

        # Take next Sequence number of shipment base on type
        pick_name = ir_sequence.get(cr, uid, 'stock.picking.' + pick_type)

        picking_id = stock_picking.create(cr, uid, {
            'name': pick_name,
            'origin': (production.origin or '').split(':')[0] + ':' + production.name,
            'type': pick_type,
            'move_type': 'one',
            'state': 'auto',
            'address_id': address_id,
            'auto_picking': True, # This one returns True ==> self._get_auto_picking(cr, uid, production),
            'company_id': production.company_id.id,
        })
        production.write({'picking_id': picking_id}, context=context)
        return picking_id

    def _purchase_bom(self, cr, uid, obj, context):
        # obj can be a order_requirement_line or temp_mrp_bom
        # Set is_temp_bom to True if obj is a temp_mrp_bom
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        purchase_order_obj = self.pool['purchase.order']
        purchase_order_line_obj = self.pool['purchase.order.line']

        # Field supplier_id is present in both temp_mrp_bom and ordreq line
        supplier_id = obj.supplier_id.id

        if not supplier_id:
            raise orm.except_orm(_(u'Error !'),
                                 _(u'There are no suppliers defined for product {0}'.format(obj.product_id.name)))
        is_temp_bom = False

        try:
            # Try if it's a ordreq line
            if obj.new_product_id:
                product_id = obj.new_product_id.id
            else:
                product_id = obj.product_id.id
        except AttributeError:
            # If we are here it's a temp_mrp_bom
            is_temp_bom = True
            product_id = obj.product_id.id

        if is_temp_bom:
            qty = obj.product_qty
            line_id = obj.order_requirement_line_id.id
        else:
            qty = obj.qty
            line_id = obj.id

        shop = obj.sale_order_id.shop_id
        shop_id = shop.id

        purchase_order_ids = purchase_order_obj.search(cr, uid, [('partner_id', '=', supplier_id),
                                                                 ('shop_id', '=', shop_id),
                                                                 ('state', '=', 'draft')], limit=1, context=context)

        if not purchase_order_ids:
            # Adding if no "similar" orders are presents
            purchase_order_values = purchase_order_obj.onchange_partner_id(cr, uid, [], supplier_id)['value']
            location_id = shop.warehouse_id.lot_stock_id.id

            order_line_values = \
                purchase_order_line_obj.onchange_product_id(cr, uid, [], purchase_order_values['pricelist_id'],
                                                            product_id, qty, uom_id=False, partner_id=supplier_id,
                                                            date_order=False,
                                                            fiscal_position_id=purchase_order_values['fiscal_position'],
                                                            date_planned=False, price_unit=False, notes=False,
                                                            context=context)['value']
            # First create order
            purchase_id = purchase_order_obj.create(cr, uid, {
                'shop_id': shop_id,
                'partner_id': supplier_id,
                'partner_address_id': purchase_order_values['partner_address_id'],
                'pricelist_id': purchase_order_values['pricelist_id'],
                'fiscal_position': purchase_order_values['fiscal_position'],
                'invoice_method': 'manual',
                'location_id': location_id,
                'payment_term': purchase_order_values['payment_term'],
            }, context=context)

            order_line_values['product_id'] = product_id
            order_line_values['order_id'] = purchase_id
            order_line_values['order_requirement_line_ids'] = [(4, line_id)]

            # Create order line and relationship with order_requirement_line
            purchase_line_id = purchase_order_line_obj.create(cr, uid, order_line_values, context)
            # Add the purchase line to ordreq LINE
            self.write(cr, uid, line_id, {'purchase_order_ids': [(4, purchase_id)],
                                          'purchase_order_line_ids': [(4, purchase_line_id)]}, context)

            if is_temp_bom:
                # If is a temp mrp bom, associate purchase line also to it
                temp_mrp_bom_obj.write(cr, uid, obj.id, {'purchase_order_id': purchase_id,
                                                         'purchase_order_line_id': purchase_line_id})
        else:
            # Extending order if I have found orders to same supplier for the same shop

            # Take first order
            present_order_id = purchase_order_ids[0]
            present_order = purchase_order_obj.browse(cr, uid, present_order_id, context)

            # Search for same product in Product lines
            purchase_order_line_ids = purchase_order_line_obj.search(cr, uid, [('order_id', 'in', purchase_order_ids),
                                                                               ('product_id', '=', product_id)],
                                                                     context=context)
            if not purchase_order_line_ids:
                # Line must be created
                order_line_values = purchase_order_line_obj.onchange_product_id(cr, uid, [], present_order.pricelist_id.id,
                                                                                product_id, qty, uom_id=False,
                                                                                partner_id=supplier_id, date_order=False,
                                                                                fiscal_position_id=False, date_planned=False,
                                                                                price_unit=False, notes=False, context=context)['value']
                order_line_values['product_id'] = product_id
                order_line_values['order_id'] = present_order_id
                # Creating a new line
                purchase_line_id = purchase_order_line_obj.create(cr, uid, order_line_values, context)
                # Link to line many2many field
                self.write(cr, uid, line_id, {'purchase_order_line_ids': [(4, purchase_line_id)]}, context)
                if is_temp_bom:
                    # If is a temp mrp bom, associate purchase line also to it
                    temp_mrp_bom_obj.write(cr, uid, obj.id, {'purchase_order_id': present_order_id,
                                                             'purchase_order_line_id': purchase_line_id})
            else:
                # Add qty to existing line
                order_line_id = purchase_order_line_ids[0]
                line = purchase_order_line_obj.browse(cr, uid, order_line_id, context)
                newqty = qty + line.product_qty
                purchase_order_line_obj.write(cr, uid, order_line_id, {'product_qty': newqty}, context)
                if is_temp_bom:
                    # If is a temp mrp bom, associate purchase line also to it
                    temp_mrp_bom_obj.write(cr, uid, obj.id, {'purchase_order_line_id': order_line_id})

    def _manufacture_bom(self, cr, uid, father, bom, context):
        mrp_production_obj = self.pool['mrp.production']
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']

        if not father:
            product = bom.product_id

            # If another production order is present and not started, queue to it
            mrp_productions = mrp_production_obj.search(cr, uid, [('product_id', '=', product.id),
                                                                  ('state', '=', 'draft')], context=context)

            if mrp_productions:
                mrp_production = mrp_productions[0]
                mrp_production_obj.write(cr, uid, mrp_production.id,
                                         {'product_qty': mrp_production.product_qty + bom.product_qty}, context)
            else:
                mrp_production_values = mrp_production_obj.product_id_change(cr, uid, [], product.id)['value']

                mrp_production_values.update({
                    'product_id': product.id,
                    'product_qty': bom.product_qty,
                    'sale_id': bom.sale_order_id.id,
                    'is_from_order_requirement': True,
                    'temp_bom_id': bom.id,
                    'level': bom.level
                })

                # Create manufacturing order
                mrp_production = mrp_production_obj.create(cr, uid, mrp_production_values, context=context)

            temp_mrp_bom_obj.write(cr, uid, bom.id, {'mrp_production_id': mrp_production})

        else:
            # TODO: TEST if father (split_mrp_productions is False)
            return
            # I am creating a "sub" product => This happens ONLY when res_partner.split_mrp_productions is False
            # Adding lines if main product manufacturing order is present
            # Reload browse record pointed by father
            father = temp_mrp_bom_obj.browse(cr, uid, father.id, context)
            mrp_production = mrp_production_obj.browse(cr, uid, father.mrp_production_id.id, context)
            if not mrp_production:
                raise orm.except_orm(_(u'Error !'),
                                     _(u'Main product order is missing for product {0}'.format(father.product_id.name)))

            # Create stock picking if not already done
            if mrp_production.picking_id:
                picking_id = mrp_production.picking_id.id
            else:
                picking_id = self._make_production_internal_shipment(cr, uid, mrp_production, context)
                mrp_production = mrp_production_obj.browse(cr, uid, father.mrp_production_id.id, context)

            # Create move line
            source_location_id = mrp_production.location_src_id.id
            destination_location_id = mrp_production.product_id.product_tmpl_id.property_stock_production.id
            if not source_location_id:
                source_location_id = mrp_production.location_src_id.id

            # shop = father.sale_order_id.shop_id
            # source_location_id = shop.warehouse_id.lot_stock_id.id

            stock_move_vals = {
                'picking_id': picking_id,
                'product_id': bom.product_id.id,
                'product_qty': bom.product_qty,
                'product_uom': bom.product_uom.id,
                'location_id': source_location_id,
                'location_dest_id': destination_location_id,
            }
            # # stock_move_id = stock_move_obj.create(cr, uid, stock_move_vals, context)
            # Create in relationship with mrp.production
            mrp_production_obj.write(cr, uid, mrp_production.id,
                                     {'move_lines': [(0, False, stock_move_vals)]}, context=context)

    def _manufacture_or_purchase_explode(self, cr, uid, father, temp, context):
        if temp.is_manufactured:
            self._manufacture_bom(cr, uid, father, temp, context)
            if not temp.is_leaf:
                if temp.level > 0:
                    self._manufacture_bom(cr, uid, False, temp, context)
                for child in temp.bom_lines:
                    self._manufacture_or_purchase_explode(cr, uid, temp, child, context)
        else:
            self._purchase_bom(cr, uid, temp, context)

    def _manufacture_or_purchase_all(self, cr, uid, ids, context):
        # line is a order_requirement_line, not a bom line
        user = self.pool['res.users'].browse(cr, uid, uid, context)

        split_orders = user.company_id.split_mrp_production

        # TODO: Maybe multi line?
        line = self.browse(cr, uid, ids, context)[0]

        if not line.temp_mrp_bom_ids:
            return

        if split_orders:
            temp = line.temp_mrp_bom_ids[0]
            # Explode orders
            self._manufacture_or_purchase_explode(cr, uid, False, temp, context)
        else:
            # Not multiorder -> First the father
            # TODO: Complete the routing with all the bom routing lines
            father_bom = line.temp_mrp_bom_ids[0]
            if father_bom.is_manufactured:
                self._manufacture_bom(cr, uid, False, father_bom, context)
                for temp in line.temp_mrp_bom_ids[1:]:
                    if temp.is_manufactured:
                        if temp.is_leaf:
                            self._manufacture_bom(cr, uid, father_bom, temp, context)
                    else:
                        self._purchase_bom(cr, uid, temp, context)
            else:
                self._purchase_bom(cr, uid, father_bom, context)

    def confirm_suppliers(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for line in self.browse(cr, uid, ids, context):
            if line.state != 'draft':
                raise orm.except_orm(_(u'Error !'),
                                     _(u'This manufacturing order has already started'))
            # line is an order_requirement_line
            if line.is_manufactured:
                self._manufacture_or_purchase_all(cr, uid, ids, context)
            else:
                self._purchase_bom(cr, uid, line, context)

            self.write(cr, uid, line.id, {'state': 'done'}, context)

            # Counting lines in Draft state, for current order requirement
            lines_draft = len(self.search(cr, uid, [('sale_order_id', '=', line.sale_order_id.id),
                                                    ('state', '=ilike', 'draft')], context=context))
            if lines_draft == 0:
                # No more draft lefts
                order_requirement_obj = self.pool['order.requirement']
                order_requirement_obj.write(cr, uid, line.order_requirement_id.id, {'state': 'done'}, context)

        return {
            'type': 'ir.actions.act_window_close'
        }

    def action_open_bom(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        line = self.browse(cr, uid, ids, context)[0]

        is_manufactured = line.is_manufactured

        if not line.new_product_id:
            product_id = line.product_id.id
            is_manufactured = True
            line_vals = line.get_suppliers(product_id, context=context)
            supplier_ids_formatted = line_vals['supplier_ids']

            line_vals.update({'new_product_id': product_id,
                              'is_manufactured': is_manufactured,
                              'supplier_ids': supplier_ids_formatted})
            self.write(cr, uid, line.id, line_vals, context)
            # Reload line
            line = self.browse(cr, uid, ids, context)[0]

        if is_manufactured and not line.temp_mrp_bom_ids:
            # if line.product_id.
            temp_ids, temp_routing = self.create_temp_mrp_bom(cr, uid, ids, line.new_product_id.id, False, 0, 0, True, True, context)
            if temp_ids:
                temp_mrp_bom_obj = self.pool['temp.mrp.bom']
                temp = temp_ids[0]
                # TODO: maybe another option create_if_leaf in create_temp_mrp_bom
                if temp['is_leaf']:
                    # I don't want to see an "empty" bom with the father only
                    temp_mrp_bom_obj.unlink(cr, uid, temp['id'], context)
                    # Must purchase
                    self.write(cr, uid, line.id, {'is_manufactured': False}, context)

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'sale_order_requirement',
                                                               'view_order_requirement_line_form')
        # Reload line
        line = self.browse(cr, uid, ids, context)[0]

        view_id = view and view[1] or False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Product BOM'),
            'res_model': 'order.requirement.line',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            'context': {'view_bom': True},
            'res_id': line.id
        }

    def onchange_temp_mrp_bom_ids(self, cr, uid, ids, temp_mrp_bom_ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']

        line_id = ids[0]

        for temp in temp_mrp_bom_ids:
            operation = temp[0]
            temp_id = temp[1]
            vals = temp[2]

            if operation == 0:
                product_id = vals['product_id']
                # father_id is already get by onchange_temp_product_id
                father_id = vals['bom_id']

                create_children = 'is_manufactured' not in vals or vals['is_manufactured']

                # Creating ==> Always level 1
                self.create_temp_mrp_bom(cr, uid, ids, product_id, father_id, 1, 9999, True, create_children, context)

            elif operation == 1:
                # Update
                temp_mrp_saved = temp_mrp_bom_obj.browse(cr, uid, temp_id, context)
                saved_product_id = temp_mrp_saved.product_id.id
                saved_level = temp_mrp_saved.level
                saved_father_id = temp_mrp_saved.bom_id.id
                saved_sequence = temp_mrp_saved.sequence

                if 'product_id' in vals:
                    # When changing product I have to recreate sub bom structure -> unlink and create.
                    product_id = vals['product_id']
                    vals['sequence'] = saved_sequence
                    create_children = ('is_manufactured' not in vals) or vals['is_manufactured']

                    # temp_mrp_bom_obj.write(cr, uid, temp_id, vals, context)
                    temp_mrp_bom_obj.unlink(cr, uid, temp_id, context)

                    temp_ids, temp_routing_ids = self.create_temp_mrp_bom(cr, uid, ids, product_id, saved_father_id,
                                                                          saved_level, saved_sequence, True, create_children,
                                                                          context)
                    # Update with given vals
                    temp_reload = temp_ids[0]
                    # if temp_reload.is_leaf:
                    #     vals['is_manufacture'] = False
                    temp_mrp_bom_obj.write(cr, uid, temp_reload['id'], vals, context)

                else:
                    # Save current with given vals
                    temp_mrp_bom_obj.write(cr, uid, temp_id, vals, context)
                    # Check if is_manufactured has changed
                    if 'is_manufactured' in vals:

                        if vals['is_manufactured']:
                            # Reloading eventually modified
                            temp_mrp = temp_mrp_bom_obj.browse(cr, uid, temp_id, context)
                            saved_sequence = temp_mrp.sequence
                            product_id = temp_mrp.product_id.id

                            # Must recalculate children but no father -> create_father=False
                            self.create_temp_mrp_bom(cr, uid, ids, product_id, temp_id, saved_level, saved_sequence, False,
                                                     True, context)
                        else:
                            # Must remove children
                            children_ids = temp_mrp_bom_obj.search(cr, uid, [('bom_id', '=', temp_id)], context=context)
                            # ondelete=cascade ensures ALL children will be removed
                            temp_mrp_bom_obj.unlink(cr, uid, children_ids, context)

            elif operation == 2:
                # Delete
                temp_mrp_bom_obj.unlink(cr, uid, temp_id, context)

        self._sort_temp_mrp_bom(cr, uid, ids, context)
        self._update_cost(cr, uid, line_id, context)
        line = self.browse(cr, uid, line_id, context)

        new_temp_ids_formatted = [t.id for t in line.temp_mrp_bom_ids]
        new_temp_routing_ids_formatted = [t.id for t in line.temp_mrp_bom_routing_ids]

        return {'value': {'temp_mrp_bom_ids': new_temp_ids_formatted,
                          'temp_mrp_bom_routing_ids': new_temp_routing_ids_formatted}
                }

    def save_suppliers(self, cr, uid, ids, context=None):
        # Dummy save function
        return True

