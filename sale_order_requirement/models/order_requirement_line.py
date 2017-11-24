# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

import tools
from tools.translate import _

import decimal_precision as dp
from mrp import mrp_bom
from openerp.osv import orm, fields
from temp_mrp_bom import temp_mrp_bom

routing_colors = ['darkblue', 'forestgreen', 'orange', 'blue', 'grey']

def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r

def fix_fields(vals):
    if vals:
        for key in vals:
            if isinstance(vals[key], tuple):
                vals[key] = vals[key][0]

class order_requirement_line(orm.Model):

    _name = 'order.requirement.line'
    _rec_name = 'product_id'

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
            elif line._temp_mrp_bom_ids:
                res[line.id] = 'cadetblue'
        return res

    def get_suppliers(self, cr, uid, ids, new_product_id, qty=0, supplier_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        supplierinfo_obj = self.pool['product.supplierinfo']
        result_dict = {}
        if new_product_id:
            product = self.pool['product.product'].browse(cr, uid, new_product_id, context)
            # --find the supplier
            supplier_info_ids = supplierinfo_obj.search(cr, uid, #[], limit=20,
                                                        [('product_id', '=', product.product_tmpl_id.id)],
                                                        order="sequence", context=context)
            supplier_infos = supplierinfo_obj.browse(cr, uid, supplier_info_ids, context=context)
            seller_ids = list(set([info.name.id for info in supplier_infos]))

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

    def update_temp_mrp_data(self, cr, uid, ids, temp, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        product_obj = self.pool['product.product']

        line_id = temp['order_requirement_line_id']
        product_id = temp['product_id']
        level = temp['level']
        qty = temp['product_qty']
        line = self.browse(cr, uid, line_id, context)
        product = product_obj.browse(cr, uid, product_id, context)

        row_color = temp_mrp_bom.get_color_bylevel(level)
        level_name = '- {} {} >'.format(str(level), ' -----' * level)

        suppliers = line.get_suppliers(product_id, qty, context=context)
        warehouse_id = line.sale_order_id.shop_id.warehouse_id.id
        stock_spare = self.generic_stock_availability(cr, uid, [], product, warehouse_id, context)
        routing_id = self.get_routing_id(cr, uid, product_id, context)
        return {
            'row_color': row_color,
            'level_name': level_name,
            'stock_availability': stock_spare['stock_availability'],
            'spare': stock_spare['spare'],
            'supplier_id': suppliers['supplier_id'],
            'supplier_ids': suppliers['supplier_ids'],
            'mrp_routing_id': routing_id
        }

    def get_routing_lines(self, cr, uid, ids, bom, temp_id, color, context=None):
        mrp_routing_workcenter_obj = self.pool['mrp.routing.workcenter']
        mrp_workcenter_obj = self.pool['mrp.workcenter']
        users_obj = self.pool['res.users']

        routing_id = self.get_routing_id(cr, uid, bom.product_id.id, context)
        workcenter_lines = mrp_routing_workcenter_obj.search_browse(cr, uid, [('routing_id', '=', routing_id)], context)
        ret_vals = []

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
                user_ids = [u.id for u in wc.user_ids]

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

    def create_temp_mrp_bom(self, cr, uid, ids, line, bom_ids, context):
        # Returns a list of VALS
        temp_mrp_bom_vals = []
        temp_mrp_routing_vals = []

        if not bom_ids:
            return []

        def _get_temp_vals(bom, bom_parent_id, father_id, level):
            return {
                'name': bom.name,
                'bom_id': father_id,
                # mrp_bom_parent_id is VERY useful for reconstructing hierarchy
                'mrp_bom_id': bom.id,
                'mrp_bom_parent_id': bom_parent_id,
                'product_id': bom.product_id.id,
                'product_qty': bom.product_qty,
                'product_uom': bom.product_uom.id,
                'product_efficiency': bom.product_efficiency,
                'product_type': bom.product_id.type,
                'is_manufactured': True,
                'company_id': bom.company_id.id,
                'position': bom.position,
                'is_leaf': not bool(bom.child_buy_and_produce_ids),
                'level': level,
                'order_requirement_line_id': line.id
            }

        def _get_rec(bom_rec, father_id, level, col):
            bom_children = bom_rec.child_buy_and_produce_ids
            if not bom_children:
                return
            for bom in bom_children:
                if True: # bom.product_id.type == 'product':
                    # level = children_levels[bom.id]['level']

                    temp_vals = _get_temp_vals(bom, bom_rec.id, father_id, level)
                    temp_additional_data = self.update_temp_mrp_data(cr, uid, [], temp_vals, context)
                    temp_vals.update(temp_additional_data)
                    temp_id = temp_mrp_bom_obj.create(cr, uid, temp_vals, context)
                    temp_vals['id'] = temp_id
                    temp_mrp_bom_vals.append(temp_vals)
                    if temp_vals['mrp_routing_id'] != 0:
                        temp_routing_vals = self.get_routing_lines(cr, uid, ids, bom, temp_id, routing_colors[col], context)
                        temp_mrp_routing_vals.extend(temp_routing_vals)
                        col = (col+1) % len(routing_colors)

                    # Even if not product I must check all children
                    _get_rec(bom, temp_id, level + 1, col)

        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        temp_mrp_routing_obj = self.pool['temp.mrp.routing']

        for bom_father in bom_ids:
            # children_levels = mrp_bom.get_all_mrp_bom_children(bom_father.child_buy_and_produce_ids, 0)

            # Main BOMs
            temp_vals = _get_temp_vals(bom_father, False, False, 0)
            temp_additional_data = self.update_temp_mrp_data(cr, uid, [], temp_vals, context)
            temp_vals.update(temp_additional_data)
            temp_id = temp_mrp_bom_obj.create(cr, uid, temp_vals, context)
            temp_vals['id'] = temp_id
            temp_mrp_bom_vals.append(temp_vals)
            # Calculate routing for Father Bom(s)
            temp_mrp_routing_vals.extend(self.get_routing_lines(cr, uid, ids, bom_father, temp_id, 'black', context))

            _get_rec(bom_father, temp_id, 1, 0)
            for routing_vals in temp_mrp_routing_vals:
                temp_mrp_routing_obj.create(cr, uid, routing_vals, context)

        return temp_mrp_bom_vals, temp_mrp_routing_vals

    def _get_or_create_temp_bom(self, cr, uid, ids, name, args, context=None):
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
            if line._temp_mrp_bom_ids:
                res[line.id]['temp_mrp_bom_ids'] = [t.id for t in line._temp_mrp_bom_ids]
                res[line.id]['temp_mrp_bom_routing_ids'] = [t.id for t in line._temp_mrp_routing_ids]
            else:
                # does not work here
                # product = line.actual_product
                if line.new_product_id:
                    product = line.new_product_id
                elif line.product_id:
                    product = line.product_id
                temp_mrp_bom_vals, temp_mrp_routing_vals = self.create_temp_mrp_bom(cr, uid, ids, line, product.bom_ids, context)
                res[line.id]['temp_mrp_bom_ids'] = temp_mrp_bom_vals
                res[line.id]['temp_mrp_bom_routing_ids'] = temp_mrp_routing_vals
        return res

    def _save_temp_mrp_bom(self, cr, uid, line_id, name, temp_mrp_bom_ids, arg, context=None):
        # TODO MAYBE USELESS: all writing in onchange_temp_mrp_bom
        return
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        # if not temp_mrp_bom_ids:
        #     return
        #
        # to_be_deleted_ids = [t[1] for t in temp_mrp_bom_ids if t[0] == 2]
        # temp_mrp_bom_obj.unlink(cr, uid, to_be_deleted_ids, context)
        #
        # is_new_set = temp_mrp_bom_ids[0][0] == 5
        # # In this case I have to care about removing all children for nested boms
        # new_temp_vals = []
        # if is_new_set:
        #     temp_by_line_ids = temp_mrp_bom_obj.search(cr, uid, [('order_requirement_line_id', '=', line_id)], context)
        #     temp_mrp_bom_obj.unlink(cr, uid, temp_by_line_ids, context)
        #     for temp in temp_mrp_bom_ids:
        #         temp_vals = temp[2]
        #         if temp_vals:
        #             if temp_mrp_bom.check_parents(temp_vals, temp_mrp_bom_ids):
        #                 # new_temp_vals.append(temp_vals)
        #                 temp_mrp_bom_obj.create(cr, uid, temp_vals, context)
        #             else:
        #                 temp_mrp_bom_obj.unlink(cr, uid, temp_vals['id'], context)
        # return

    def _save_temp_mrp_bom_routing(self, cr, uid, line_id, name, temp_routing_vals, arg, context=None):
        # TODO MAYBE USELESS: all writing in onchange_temp_mrp_bom
        return
        # context = context or self.pool['res.users'].context_get(cr, uid)
        # temp_mrp_bom_obj = self.pool['temp.mrp.routing']
        #
        # if not temp_routing_vals:
        #     return
        #
        # # If the first record is [5, False, False] I am creating
        # is_creation = temp_routing_vals[0][0] == 5
        # if is_creation:
        #     temp_mrp_bom_obj.write(cr, uid, temp_routing_vals, context)
        #     # IF I am creating, start cycle from second item (first is shown above)
        #     # for val in temp_routing_vals[1:]:
        #     #     if val:
        #     #         temp_vals = val[2]
        #     #         temp_vals['order_requirement_line_id'] = line_id
        #     #         new_id = temp_mrp_bom_obj.create(cr, uid, temp_vals, context)
        #     #         temp_vals['id'] = new_id
        #     #         # map[ old ID ] => vals
        #     #         bom_map[temp_vals['mrp_bom_id']] = temp_vals
        # else:
        #     # I am updating
        #     pass
        #     # for val in temp_mrp_bom_vals:
        #     #     if val[0] == 1:
        #     #         # Only items in this form are updating: [1,ID,{values}]
        #     #         temp_id = val[1]
        #     #         temp_vals = val[2]
        #     #         temp_mrp_bom_obj.write(cr, uid, temp_id, temp_vals, context)
        # return

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
        'purchase_order_line_ids': fields.many2many('purchase.order.line', string='Purchase Order lines'),
        '_temp_mrp_bom_ids': fields.one2many('temp.mrp.bom', 'order_requirement_line_id', 'BoM Hierarchy'),
        'temp_mrp_bom_ids': fields.function(_get_or_create_temp_bom, multi='temp_mrp_bom', relation='temp.mrp.bom', string="BoM Hierarchy",
                                            method=True, type='one2many', fnct_inv=_save_temp_mrp_bom,
                                            readonly=True, states={'draft': [('readonly', False)]}),
        '_temp_mrp_routing_ids': fields.one2many('temp.mrp.routing', 'order_requirement_line_id', 'BoM Routing'),
        'temp_mrp_bom_routing_ids': fields.function(_get_or_create_temp_bom, multi='temp_mrp_bom', relation='temp.mrp.routing',
                                                    string="BoM Routing", method=True, type='one2many', readonly=True,
                                                    states={'draft': [('readonly', False)]},
                                                    fnct_inv=_save_temp_mrp_bom_routing)
    }

    _defaults = {
        'state': 'draft',
        'sequence': 10,
    }

    # def fields_get(self, cr, uid, allfields=None, context=None):
        # Useful for showing bom only if the button is pressed, not the click on the line
        # context = context or self.pool['res.users'].context_get(cr, uid)
        # ret = super(order_requirement_line, self).fields_get(cr, uid, allfields=allfields, context=context)
        # view_bom = 'view_bom' in context and context['view_bom']
        # ret['temp_mrp_bom_ids']['invisible'] = not view_bom
        # ret['temp_mrp_bom_routing_ids']['invisible'] = not view_bom
        # ret['confirm_suppliers']['invisible'] = not view_bom
        # return ret

    # def onchange_is_manufactured(self, cr, uid, ids, is_manufactured, temp_mrp_bom_ids, context=None):
    #     # Synchronize the first BOM line "is_manufactured" flag with the line one
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     temp_mrp_bom_obj = self.pool['temp.mrp.bom']
    #     for line in self.browse(cr, uid, ids, context):
    #         try:
    #             # First line, second item in list is ID
    #             father_bom_id = temp_mrp_bom_ids[0][2]
    #             temp_mrp_bom_obj.write(cr, uid, father_bom_id, {'is_manufactured': is_manufactured}, context)
    #         except IndexError:
    #             # TODO: Log something
    #             pass
    #     return {}

    def onchange_product_id(self, cr, uid, ids, new_product_id, qty=0, supplier_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result_dict = self.get_suppliers(cr, uid, ids, new_product_id, qty, supplier_id, context)

        if new_product_id:
            product = self.pool['product.product'].browse(cr, uid, new_product_id, context)

            # Update BOM according to new product
            # Removing existing temp mrp bom
            line = self.browse(cr, uid, ids, context)[0]  # MUST BE ONE LINE
            if line._temp_mrp_bom_ids:
                temp_mrp_bom_obj = self.pool['temp.mrp.bom']
                temp_mrp_bom_ids = [temp['id'] for temp in line._temp_mrp_bom_ids]
                temp_mrp_bom_obj.unlink(cr, uid, temp_mrp_bom_ids, context)

            if product.bom_ids:
                self.write(cr, uid, line.id, {'new_product_id': product.id}, context)
                temp_mrp_bom_vals, temp_mrp_bom_routing_vals = self.create_temp_mrp_bom(cr, uid, ids, line, product.bom_ids, context)

                temp_mrp_bom_ids = [(0, False, t) for t in temp_mrp_bom_vals]
                temp_mrp_bom_routing_ids = [(0, False, t) for t in temp_mrp_bom_routing_vals]

                result_dict.update({
                    'temp_mrp_bom_ids': temp_mrp_bom_ids,
                    'temp_mrp_bom_routing_ids': temp_mrp_bom_routing_ids,
                    'view_bom': True
                    # 'is_manufactured': True
                })
        else:
            # TODO: result_dict with false inside
            result_dict['view_bom'] = False
        return {'value': result_dict}

    def _purchase_bom(self, cr, uid, obj, is_temp_bom, context):
        # obj can be a order_requirement_line or temp_mrp_bom
        # Set is_temp_bom to True if obj is a temp_mrp_bom
        purchase_order_obj = self.pool['purchase.order']
        purchase_order_line_obj = self.pool['purchase.order.line']

        supplier_id = obj.supplier_id.id

        if not supplier_id:
            raise orm.except_orm(_(u'Error !'),
                                 _(u'There are no suppliers defined for product {0}'.format(obj.product_id.name)))

        try:
            if obj.new_product_id:
                product_id = obj.new_product_id.id
            else:
                product_id = obj.product_id.id
        except:
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
            purchase_order_line_obj.create(cr, uid, order_line_values, context)

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
                                                            product_id, qty, uom_id=False, partner_id=supplier_id,
                                                            date_order=False,
                                                            fiscal_position_id=False, date_planned=False,
                                                            price_unit=False, notes=False, context=context)['value']
                order_line_values['product_id'] = product_id
                order_line_values['order_id'] = present_order_id
                # Creating a new line and link to many2many field
                self.write(cr, uid, obj.id, {'purchase_order_line_ids': [(0, 0, order_line_values)]}, context)
            else:
                # Add qty to existing line
                order_line_id = purchase_order_line_ids[0]
                line = purchase_order_line_obj.browse(cr, uid, order_line_id, context)
                newqty = qty + line.product_qty
                purchase_order_line_obj.write(cr, uid, order_line_id, {'product_qty': newqty}, context)

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

    def _manufacture_bom(self, cr, uid, father, bom, context):
        mrp_production_obj = self.pool['mrp.production']
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']

        if not father:
            # I am creating a "main" product
            mrp_production_workcenter_line_obj = self.pool['mrp.production.workcenter.line']
            product = bom.product_id
            mrp_production_values = mrp_production_obj.product_id_change(cr, uid, [], product.id)['value']

            mrp_production_values['product_id'] = product.id
            mrp_production_values['sale_id'] = bom.sale_order_id.id

            # Create manufacturing order
            mrp_production_id = mrp_production_obj.create(cr, uid, mrp_production_values, context=context)
            temp_routing_vals = self._get_temp_routing(bom)
            for rout in temp_routing_vals:
                rout['production_id'] = mrp_production_id
                mrp_production_workcenter_line_obj.create(cr, uid, rout, context)
            temp_mrp_bom_obj.write(cr, uid, bom.id, {'mrp_production_id': mrp_production_id})
            return

        # I am creating a "sub" product

        # Adding lines if main product manufacturing order is present
        # Reload browse record pointed by father
        father = temp_mrp_bom_obj.browse(cr, uid, father.id, context)
        mrp_production_id = mrp_production_obj.browse(cr, uid, father.mrp_production_id.id, context)
        if not mrp_production_id:
            raise orm.except_orm(_(u'Error !'),
                                 _(u'Main product order is missing for product {0}'.format(father.product_id.name)))
        # Create move line
        shop = father.sale_order_id.shop_id
        location = shop.warehouse_id.lot_stock_id

        stock_move_vals = {
            'product_id': bom.product_id.id,
            'product_qty': bom.product_qty,
            'product_uom': bom.product_uom.id,
            'location_id': location.id,
            'location_dest_id': 1,  # todo location_dest_id
        }
        # stock_move_id = stock_move_obj.create(cr, uid, stock_move_vals, context)
        # Create in relationship with mrp.production
        mrp_production_obj.write(cr, uid, mrp_production_id.id,
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
            self._purchase_bom(cr, uid, temp, True, context)

    def _manufacture_or_purchase_all(self, cr, uid, ids, line, context):
        # line is a order_requirement_line, not a bom line
        # TODO: use ids, not line?
        # TODO: put multi_orders as res.company flag
        multi_orders = True

        if not line._temp_mrp_bom_ids:
            return

        if multi_orders:
            temp = line._temp_mrp_bom_ids[0]
            # Explode orders
            self._manufacture_or_purchase_explode(cr, uid, False, temp, context)
        else:
            # TODO: Complete the routing with all the bom routing lines
            # Not multiorder -> First the father
            father_bom = line._temp_mrp_bom_ids[0]
            if father_bom.is_manufactured:
                self._manufacture_bom(cr, uid, False, father_bom, context)
                for temp in line._temp_mrp_bom_ids[1:]:
                    if temp.is_manufactured:
                        if temp.is_leaf:
                            self._manufacture_bom(cr, uid, father_bom, temp, context)
                    else:
                        self._purchase_bom(cr, uid, temp, True, context)
            else:
                self._purchase_bom(cr, uid, father_bom, True, context)

    def confirm_suppliers(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # TODO: Now everything is a BOM, no need to "manufacture lines"
        for line in self.browse(cr, uid, ids, context):
            if line.state != 'draft':
                raise orm.except_orm(_(u'Error !'),
                                     _(u'This manufacturing order has already started'))
            # line is an order_requirement_line
            if line.is_manufactured:
                self._manufacture_or_purchase_all(cr, uid, ids, line, context)
            else:
                self._purchase_bom(cr, uid, line, False, context)

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
        if not line.new_product_id:
            self.write(cr, uid, line.id, {'new_product_id': line.product_id.id,
                                          'is_manufactured': True}, context)

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'sale_order_requirement',
                                                               'view_order_requirement_line_form')
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

    def onchange_temp_mrp_bom_ids_NO(self, cr, uid, ids, temp_mrp_bom_ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        line = self.browse(cr, uid, ids, context)[0]
        self.write(cr, uid, ids, {'temp_mrp_bom_ids': temp_mrp_bom_ids})

        # Reload list (some related child temp mrp boms could have been deleted)
        new_temp_vals = []
        for temp in line._temp_mrp_bom_ids:
            vals = temp_mrp_bom_obj.read(cr, uid, temp.id, [], context)
            if vals:
                fix_fields(vals)
                new_temp_vals.append(vals)

        new_temp_mrp_bom_ids = [(0, False, t) for t in new_temp_vals]

        return {'value': {'temp_mrp_bom_ids': new_temp_mrp_bom_ids}}

    def onchange_temp_mrp_bom_ids(self, cr, uid, ids, temp_mrp_bom_ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']

        # If in presence of a new unsaved set of mrp boms, list will start with [5,0,False]
        # and all items in list will be [4,id,False]
        is_new_set = not temp_mrp_bom_ids or temp_mrp_bom_ids[0][0] == 5
        new_temp_vals = []
        new_temp_vals_formatted = []
        if is_new_set:
            # When is_new_set is True, I have to check all present boms and remove the missing
            # Cycle through all and remove childs
            for temp in temp_mrp_bom_ids:
                vals = temp[2]
                if vals:
                    temp_id = vals['id']
                    if temp_mrp_bom.check_parents(vals, temp_mrp_bom_ids):
                        new_temp_vals.append(vals)
                    else:
                        temp_mrp_bom_obj.unlink(cr, uid, temp_id, context)
            # Not finished yet: I have to manually remove all bom not leaf and with no children
            line = self.browse(cr, uid, ids, context)[0]
            for temp in line._temp_mrp_bom_ids:
                if not temp.is_leaf:
                    if not temp_mrp_bom_obj.has_children(temp, new_temp_vals) and temp.is_manufactured:
                        temp_mrp_bom_obj.unlink(cr, uid, temp.id, context)
        else:
            for temp in temp_mrp_bom_ids:
                operation = temp[0]
                temp_id = temp[1]
                vals = temp[2]

                if operation == 1:
                    # Update
                    temp_mrp_bom_obj.write(cr, uid, temp_id, vals, context)
                elif operation == 2:
                    # Delete
                    temp_mrp_bom_obj.unlink(cr, uid, temp_id, context)
            line = self.browse(cr, uid, ids, context)[0]
            # Reload list (some related child temp mrp boms could have been deleted)
            for temp in line._temp_mrp_bom_ids:
                vals = temp_mrp_bom_obj.read(cr, uid, temp.id, [], context)
                if vals:
                    fix_fields(vals)
                    new_temp_vals.append(vals)

        # TODO: Update routings
        # new_temp_mrp_bom_ids = [(5, 0, False)]
        line = self.browse(cr, uid, ids, context)[0]

        if not new_temp_vals_formatted:
            new_temp_vals_formatted = [(5, 0, False)]
            new_temp_vals_formatted.extend([(0, t['id'], t) for t in new_temp_vals])

        return {'value': {'temp_mrp_bom_ids': new_temp_vals_formatted}}

    # def onchange_temp_mrp_bom_routing_ids(self, cr, uid, ids, temp_mrp_bom_ids, context):
    #     context = context or self.pool['res.users'].context_get(cr, uid)

    def save_suppliers(self, cr, uid, ids, context=None):
        # Dummy save function
        return True

