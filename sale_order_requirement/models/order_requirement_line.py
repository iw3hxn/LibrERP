# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

import datetime

import decimal_precision as dp
from openerp.osv import orm, fields

from tools.translate import _
from . import temp_mrp_bom

class order_requirement_line(orm.Model):

    _name = 'order.requirement.line'

    _rec_name = 'product_id'

    def _get_actual_product(self, cr, uid, ids, name = None, args = None, context=None):
        line = self.browse(cr, uid, ids, context)[0]
        if line.new_product_id:
            return line.new_product_id
        else:
            return line.product_id

    def _stock_availability(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        warehouse_order_point_obj = self.pool['stock.warehouse.orderpoint']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            spare = 0
            warehouse = line.sale_order_id.shop_id.warehouse_id
            product = self._get_actual_product(cr, uid, ids)
            order_point_ids = warehouse_order_point_obj.search(cr, uid, [('product_id', '=', product.id),
                                                                         ('warehouse_id', '=', warehouse.id)], context=context, limit=1)
            if order_point_ids:
                spare = warehouse_order_point_obj.browse(cr, uid, order_point_ids, context)[0].product_min_qty

            res[line.id] = {
                'stock_availability': product.id and product.type != 'service' and product.qty_available or False,
                'spare': spare,
            }
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

    def get_children(self, object, level=0):
        result = {}

        def _get_rec(object, level):
            for l in object:
                res = {'name': l.name,
                       'pname': l.product_id.name,
                       'pcode': l.product_id.default_code,
                       'pqty': l.product_qty,
                       'uname': l.product_uom.name,
                       'code': l.code,
                       'level': level
                       }

                result[l.id] = res
                if l.child_buy_and_produce_ids:
                    if level < 6:
                        level += 1
                    _get_rec(l.child_buy_and_produce_ids, level)
                    if 0 < level < 6:
                        level -= 1
            return result

        children = _get_rec(object, level)

        return children

    def get_temp_mrp_bom(self, cr, uid, bom_ids, context):
        # Returns a list of VALS
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_vals = []

        if not bom_ids:
            return []

        for bom_father in bom_ids:
            children_levels = self.get_children(bom_father.child_buy_and_produce_ids, 0)

            def _get_rec(bom_rec):
                bom_children = bom_rec.child_buy_and_produce_ids
                if not bom_children:
                    return
                colors = ['black', 'blue', 'cadetblue', 'grey']
                for bom in bom_children:
                    if bom.product_id.type == 'product':
                        # coolname = u' {1} - {0} {2}'.format(bom.id, bom_rec.id, bom.name)
                        level = children_levels[bom.id]['level']
                        complete_name = bom.name
                        try:
                            row_color = colors[level]
                        except KeyError:
                            row_color = 'grey'
                        if level > 0:
                            complete_name = '-----' * level + '> ' + complete_name
                        newbom_vals = {
                            'name': bom.name,
                            # tmp_* Could be useful for reconstructing hierarchy
                            'tmp_id': bom.id,
                            'tmp_parent_id': bom_rec.id,
                            'complete_name': complete_name,
                            'name': bom.name,
                            # 'bom_id': bom.bom_id.id,
                            'product_id': bom.product_id.id,
                            'product_qty': bom.product_qty,
                            'product_uom': bom.product_uom.id,
                            'product_efficiency': bom.product_efficiency,
                            'product_type': bom.product_id.type,
                            'routing_id': bom.routing_id.id,
                            'company_id': bom.company_id.id,
                            'position': bom.position,
                            'is_leaf': not bool(bom.child_buy_and_produce_ids),
                            'level': level,
                            'row_color': row_color
                        }
                        temp_mrp_bom_vals.append(newbom_vals)
                    # Even if not product I must check all children
                    _get_rec(bom)

            _get_rec(bom_father)
        return temp_mrp_bom_vals

    def _get_or_create_temp_mrp(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        view_bom = 'view_bom' in context and context['view_bom']
        if not view_bom:
            return {}
        res = {}
        for line in self.browse(cr, uid, ids, context):
            if line._temp_mrp_bom_ids:
                res[line.id] = [t.id for t in line._temp_mrp_bom_ids]
            else:
                # does not work here
                # product = line.actual_product
                if line.new_product_id:
                    product = line.new_product_id
                elif line.product_id:
                    product = line.product_id
                temp_mrp_bom_vals = self.get_temp_mrp_bom(cr, uid, product.bom_ids, context)
                res[line.id] = temp_mrp_bom_vals
        return res

    def _save_temp_mrp_bom(self, cr, uid, line_id, name, temp_mrp_bom_vals, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']

        if not temp_mrp_bom_vals:
            return

        # If the first record is [5, False, False] I am creating
        is_creation = temp_mrp_bom_vals[0][0] == 5
        if is_creation:
            bom_map = {}
            # IF I am creating, start cycle from second item (first is shown above)
            for val in temp_mrp_bom_vals[1:]:
                if val:
                    temp_vals = val[2]
                    temp_vals['order_requirement_line_id'] = line_id
                    new_id = temp_mrp_bom_obj.create(cr, uid, temp_vals, context)
                    temp_vals['id'] = new_id
                    # map[ old ID ] => vals
                    bom_map[temp_vals['tmp_id']] = temp_vals
            # Now creating hierarchy
            # for old_id in bom_map:
            #     bom = bom_map[old_id]
            #     old_parent_id = bom['tmp_parent_id']
            #     try:
            #         new_parent_id = bom_map[old_parent_id]['id']
            #         bom['parent_id'] = new_parent_id
            #         temp_mrp_bom_obj.write(cr, uid, bom['id'], bom, context)
            #     except KeyError as e:
            #         print e.message

            for b in bom_map:
                print bom_map[b]['id'], bom_map[b]['tmp_parent_id']

        else:
            # I am updating
            for val in temp_mrp_bom_vals:
                if val[0] == 1:
                    # Only items in this form are updating: [1,ID,{values}]
                    temp_id = val[1]
                    temp_vals = val[2]
                    temp_mrp_bom_obj.write(cr, uid, temp_id, temp_vals, context)
        a = 1
        return

    _columns = {
        'new_product_id': fields.many2one('product.product', 'Choosen Product', readonly=True,
                                          states={'draft': [('readonly', False)]}),
        'product_id': fields.many2one('product.product', 'Original Product', readonly=True),
        'actual_product': fields.function(_get_actual_product, store=False),
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
        'temp_mrp_bom_ids': fields.function(_get_or_create_temp_mrp, relation='temp.mrp.bom', string="BoM Hierarchy",
                                            method=True, type='one2many', fnct_inv=_save_temp_mrp_bom,
                                            readonly=True, states={'draft': [('readonly', False)]}),
    }

    _defaults = {
        'state': 'draft',
        'sequence': 10,
    }

    def fields_get(self, cr, uid, allfields=None, context=None):
        # Useful for showing bom only if the button is pressed, not the click on the line
        context = context or self.pool['res.users'].context_get(cr, uid)
        ret = super(order_requirement_line, self).fields_get(cr, uid, allfields=allfields, context=context)
        view_bom = 'view_bom' in context and context['view_bom']
        ret['temp_mrp_bom_ids']['invisible'] = not view_bom
        # ret['confirm_suppliers']['invisible'] = not view_bom

        return ret

    def onchange_product_id(self, cr, uid, ids, new_product_id, qty=0, supplier_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        supplierinfo_obj = self.pool['product.supplierinfo']
        # result_dict = {}
        result_dict = {'temp_mrp_bom_ids': []}
        if new_product_id:
            product = self.pool['product.product'].browse(cr, uid, new_product_id, context)
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

            # Update BOM according to new product
            # Removing existing temp mrp bom
            line = self.browse(cr, uid, ids, context)[0]
            if line._temp_mrp_bom_ids:
                temp_mrp_bom_obj = self.pool['temp.mrp.bom']
                temp_mrp_bom_obj.unlink(cr, uid, line._temp_mrp_bom_ids, context)

            if product.bom_ids:
                temp_mrp_bom_vals = self.get_temp_mrp_bom(cr, uid, product.bom_ids, context)
                result_dict.update({
                    'temp_mrp_bom_ids': temp_mrp_bom_vals,
                    'view_bom': True,
                    'is_manufactured': True
                })
            else:
                result_dict['view_bom'] = False

        else:
            result_dict.update({
                'supplier_id': False,
                'supplier_ids': [],
            })

        return {'value': result_dict}

    def _purchase(self, cr, uid, obj, is_temp_bom, context):
        # obj can be a order_requirement_line or temp_mrp_bom
        # Set is_temp_bom to True if obj is a temp_mrp_bom
        purchase_order_obj = self.pool['purchase.order']
        purchase_order_line_obj = self.pool['purchase.order.line']

        supplier_id = obj.supplier_id.id

        if not supplier_id:
            raise orm.except_orm(_(u'Error !'),
                                 _(u'There are no suppliers defined for product {0}'.format(obj.product_id.name)))

        if obj.new_product_id:
            product_id = obj.new_product_id.id
        else:
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

    def _manufacture_main_product(self, cr, uid, line, context):
        mrp_production_obj = self.pool['mrp.production']

        product = line.actual_product

        # Always add manufacturing orders, same products can have different boms
        mrp_production_values = mrp_production_obj.product_id_change(cr, uid, [], product.id)['value']

        # Create manufacturing order
        mrp_production_values['product_id'] = product.id
        mrp_proudction_id = mrp_production_obj.create(cr, uid, mrp_production_values, context=context)

    def _manufacture_bom(self, cr, uid, line, bom, context):
        # TODO: this will do one at a time, maybe can be enhanced!
        mrp_production_obj = self.pool['mrp.production']

        main_product = line.actual_product

        mrp_production_ids = mrp_production_obj.search(cr, uid, [('product_id', '=', main_product.id),
                                                                 ('state', '=', 'draft')])
        if not mrp_production_ids:
            raise orm.except_orm(_(u'Error !'),
                                 _(u'Main product order is missing for product {0}'.format(main_product.name)))

        # Adding lines if main product manufacturing order is present
        # Take first
        mrp_production_id = mrp_production_ids[0]
        # Create move line
        shop = line.sale_order_id.shop_id
        location = shop.warehouse_id.lot_stock_id

        stock_move_vals = {
            'product_id': bom.product_id.id,
            'product_qty': bom.product_qty,
            'product_uom': bom.product_uom.id,
            'location_id': location.id,
            'location_dest_id': 1,
            # todo ask
        }
        # stock_move_id = stock_move_obj.create(cr, uid, stock_move_vals, context)
        # Create in relationship with mrp.production
        mrp_production_obj.write(cr, uid, mrp_production_id,
                                 {'move_lines': [(0, False, stock_move_vals)]}, context=context)

    def _manufacture_all(self, cr, uid, line, context):
        # First set main product to manufacture
        self._manufacture_main_product(cr, uid, line, context)
        # Then set all bom lines product to manufacture (or buy)
        for temp in line._temp_mrp_bom_ids:
            if temp.is_manufactured:
                self._manufacture_bom(cr, uid, line, temp, context)
            else:
                # This is OK, it works, uncomment
                self._purchase(cr, uid, temp, True, context)
                pass

    def confirm_suppliers(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)

        for line in self.browse(cr, uid, ids, context):
            if line.is_manufactured:
                self._manufacture_all(cr, uid, line, context)
            else:
                self._purchase(cr, uid, line, False, context)

            self.write(cr, uid, line.id, {'state': 'done'}, context)

            # Counting lines in Draft state, for current order requirement
            lines_draft = len(self.search(cr, uid, [('sale_order_id', '=', line.sale_order_id.id),
                                                    ('state', '=ilike', 'draft')], context=context))
            if lines_draft == 0:
                # No more draft lefts
                order_requirement_obj = self.pool['order.requirement']
                order_requirement_obj.write(cr, uid, line.order_id.id, {'state': 'done'}, context)

        return {
            'type': 'ir.actions.act_window_close'
        }

    def action_open_bom(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        line = self.browse(cr, uid, ids, context)[0]

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
            'context': {'view_bom': True, 'trunk_product': True},
            'res_id': line.id
        }

    def onchange_temp_mrp_bom_ids(self, cr, uid, ids, temp_mrp_bom_ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        line = self.browse(cr, uid, ids, context)[0]
        # If in presence of a new unsaved set of mrp boms, list will start with [5,0,False]
        is_new_set = temp_mrp_bom_ids[0][0] == 5
        new_temp_mrp_bom_ids = []
        for t in temp_mrp_bom_ids:
            ta = temp_mrp_bom.get_all_children_ids(t[2], temp_mrp_bom_ids)
            a = ta
        if True or is_new_set:
            # Cycle through all
            for temp in temp_mrp_bom_ids:
                vals = temp[2]
                if temp_mrp_bom.check_parents(vals, temp_mrp_bom_ids):
                    new_temp_mrp_bom_ids.append(vals)

        return {'value': {'temp_mrp_bom_ids': new_temp_mrp_bom_ids}}

    def save_suppliers(self, cr, uid, ids, context=None):
        # Dummy save function
        return True

