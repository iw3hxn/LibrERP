# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from datetime import datetime

from dateutil.relativedelta import relativedelta
from openerp.addons.sale_order_requirement.models.order_requirement import STATE_SELECTION

import decimal_precision as dp
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from ..util import rounding

default_row_colors = ['black', 'darkblue', 'cadetblue', 'grey']


class TempMrpBom(orm.Model):
    _name = 'temp.mrp.bom'
    _description = "Temporary Bom Line"

    stock_availability = {}

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(TempMrpBom, self).write(cr, uid, ids, vals, context)
        if context.get('active_model') == 'order.requirement.line' and isinstance(ids, (int, long)) and vals.get('product_qty'):
            product_qty = vals['product_qty']
            for line in self.browse(cr, uid, ids, context).bom_lines:
                if line.state != 'draft':
                    raise orm.except_orm(
                        _('Error'),
                        _('I can change QTY on on draft line'))
                new_qty = line.original_qty * product_qty
                line.write({'product_qty': new_qty})

        return res

    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = []
        if not ids:
            return res
        if isinstance(ids, (int, long)):
            ids = [ids]
        # for bom_required in self.browse(cr, uid, ids, context=context):
        #     name = u"{}: {} {}".format(bom_required.sale_order_id.name, bom_required.product_qty, bom_required.product_uom.name)
        #     res.append((bom_required.id, name))

        for bom_required in self.read(cr, uid, ids, ['sale_order_id', 'product_qty', 'product_uom'], context=context):
            name = u"{}: {} {}".format(bom_required['sale_order_id'][1], bom_required['product_qty'], bom_required['product_uom'][1])
            res.append((bom_required['id'], name))
        return res

    # This is called also when loading saved temp mrp boms,
    # during creation see get_temp_mrp_bom
    def _stock_availability(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        order_requirement_line_obj = self.pool['order.requirement.line']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.id in self.stock_availability:
                res[line.id] = self.stock_availability[line.id]
                continue
            product_id = line.product_id.id
            warehouse_id = line.sale_order_id.shop_id.warehouse_id.id
            res[line.id] = order_requirement_line_obj.generic_stock_availability(cr, uid, ids, product_id, warehouse_id, context=context)
            # todo check. First Line must be equal
            # if line.level == 0:
            #     res[line.id]['stock_availability'] -= line.product_qty  # i don't have to count self
            self.stock_availability[line.id] = res[line.id]
        return res

    def _compute_position(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.mrp_bom_id and line.mrp_bom_id.position or ''
        return res

    def _is_out_of_stock(self, cr, uid, ids, name, args, context=None):
        # Return True if stock is less than spare
        res = {}
        for line in self.read(cr, uid, ids, ['stock_availability', 'spare'], context=context):
            res[line['id']] = line['stock_availability'] < line['spare']
        return res

    def _get_connected_document(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.read(cr, uid, ids, ['purchase_order_id', 'mrp_production_id'], context=context):
            res[line['id']] = line['purchase_order_id'] and line['purchase_order_id'][1] or line[
                'mrp_production_id'] and line['mrp_production_id'][1] or ''
        return res

    def _get_temp_mrp_bom_action(self, cr, uid, ids, name, args, context=None):
        # Return a string describing whether a product is being bought or produced
        res = {}
        for line in self.read(cr, uid, ids, ['is_manufactured', 'buy'], context=context):
            if line['is_manufactured']:
                preview = _('Produce')
            elif line['buy']:
                preview = _('Buy')
            else:
                preview = _('Stock')
            res[line['id']] = preview
        return res

    # This is called also when loading saved temp mrp boms,
    # during creation see get_temp_mrp_bom
    def _get_routing(self, cr, uid, ids, field_name, arg, context):
        res = {}
        mrp_bom_obj = self.pool['mrp.bom']
        for line in self.read(cr, uid, ids, ['product_id'], context):
            product_id = line['product_id'][0]
            routing_id = mrp_bom_obj.search_browse(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], context)
            # Here routing_id must be a browse record, not a list
            res[line['id']] = routing_id
        return res

    def _is_belowspare(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for line in self.read(cr, uid, ids, ['stock_availability', 'spare'], context):
            res[line['id']] = line['stock_availability'] < line['spare']
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
        for line in self.read(cr, uid, ids, ['level'], context):
            row_color = self.get_color_bylevel(line['level'])
            res[line['id']] = row_color
        return res

    def action_toggle_manufactured(self, cr, uid, ids, context):
        if not ids:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]
        line = self.read(cr, uid, ids[0], ['level', 'is_leaf', 'is_manufactured', 'order_requirement_line_id', 'state'], context)
        if not line:
            raise orm.except_orm(
                _('Error'),
                _('Press "Reload & Preview" Button'))
        if line['state'] != 'draft':
            return False

        if line['level'] == 0 or line['is_leaf']:
            return True
        temp_dict = {'is_manufactured': not line['is_manufactured']}
        self.write(cr, uid, [ids[0]], temp_dict, context=context)

        ordreqline_model = self.pool['order.requirement.line']
        # Build update value [1, ID, vals]
        temp_vals = [1, line['id'], temp_dict]
        ordreqline_model.onchange_temp_mrp_bom_ids(cr, uid, line['order_requirement_line_id'][0], temp_mrp_bom_ids=[temp_vals], context=context)
        return True

    def action_toggle_buy(self, cr, uid, ids, context):
        if not ids:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]
        line = self.read(cr, uid, ids[0], ['level', 'is_manufactured', 'buy', 'state'], context)
        if not line:
            raise orm.except_orm(
                _('Error'),
                _('Press "Reload & Preview" Button'))
        if line['state'] != 'draft':
            return False

        if line['level'] == 0 or line['is_manufactured']:
            return True
        self.write(cr, uid, [ids[0]], {
            'buy': not line['buy'],
            'purchase_order_line_id': False,
            'purchase_order_id': False
        }, context=context)
        return True

    def update_supplier(self, cr, uid, ids, context):
        # todo check why not work!!
        line = self.browse(cr, uid, ids, context)[0]
        result_dict = self.pool['order.requirement.line'].get_suppliers(cr, uid, ids, line.product_id, context)
        supplier_ids_formatted = result_dict['supplier_ids']
        line.write({'supplier_ids': supplier_ids_formatted})
        return True

    _columns = {
        'active': fields.boolean(required=True),
        'state': fields.selection(STATE_SELECTION, 'State', required=True, default='draft'),
        'name': fields.char('Name', size=160, readonly=True),
        'type': fields.selection([('normal', 'Normal BoM'), ('phantom', 'Sets / Phantom')], 'BoM Type', required=True,
                                 help="If a sub-product is used in several products, it can be useful to create its own BoM. " \
                                      "Though if you don't want separated production orders for this sub-product, select Set/Phantom as BoM type. " \
                                      "If a Phantom BoM is used for a root product, it will be sold and shipped as a set of components, instead of being produced."),
        'level_name': fields.char('Level', readonly=True),
        'order_requirement_line_id': fields.many2one('order.requirement.line', 'Order requirement line', required=True, index=True,
                                                     ondelete='cascade', select=True, auto_join=True),
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
        'partial_cost': fields.float('Partial Cost', readonly=True),
        'cost': fields.float('Cost', readonly=True),
        'product_type': fields.char('Pr.Type', size=10, readonly=True),
        'sale_order_id': fields.related('order_requirement_line_id', 'order_requirement_id', 'sale_order_id', auto_join=True,
                                        string='Sale Order', relation='sale.order', type='many2one', readonly=True),
        # mrp_bom_id and mrp_bom_parent_id point to the original mrp bom
        'mrp_bom_id': fields.many2one('mrp.bom', string="MRP BOM"),
        'mrp_bom_parent_id': fields.many2one('mrp.bom', string="Parent MRP BOM"),
        'bom_position': fields.function(_compute_position, type='char', string='Internal Reference'),
        # 'bom_position': fields.related('mrp_bom_id', 'position', String='Internal Reference', type='char'),
        # mrp_routing_id is a relation with ORIGINAL routing (but we make a copy)
        'mrp_routing_id': fields.many2one('mrp.routing', string='Routing', auto_join=True, readonly=True),
        'temp_mrp_routing_lines': fields.one2many('temp.mrp.routing', 'temp_mrp_bom_id', 'Routing Lines'),
        'mrp_production_id': fields.many2one('mrp.production', string='Manufacturing Order', select=True),
        # 'mrp_production_line_id': fields.many2one('mrp.production.???', string='Manufacturing Order'),
        'purchase_order_id': fields.many2one('purchase.order', string='Purchase Order', select=True),
        'purchase_order_line_id': fields.many2one('purchase.order.line', string='Purchase Order Line', select=True),
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
        'is_out_of_stock': fields.function(_is_out_of_stock, method=True, type='boolean', string='Out of Stock', readonly=True),
        'temp_mrp_bom_action': fields.function(_get_temp_mrp_bom_action, method=True, type='char', string='Action', readonly=True),
        'connected_document': fields.function(_get_connected_document, method=True, type='char', string="Document", readonly=True),
        'user_id': fields.many2one('res.users', 'User'),
    }

    _order = 'sequence,level,id'

    _defaults = {
        'active': True,
        'is_manufactured': True,
        'level': 1,  # Useful for insertion of new temp mrp boms
        'state': 'draft',
        'product_qty': 1
    }

    def _manufacture_bom(self, cr, uid, temp, context):
        mrp_production_model = self.pool['mrp.production']
        uom_model = self.pool['product.uom']

        product = temp.product_id

        user_id = temp.user_id or temp.order_requirement_line_id.user_id or False

        # Search for another production order for the same sale order
        mrp_production_domain = [('product_id', '=', product.id),
                                 ('sale_id', '=', temp.sale_order_id.id),
                                 ('state', '=', 'draft')]
        if user_id:
            mrp_production_domain.append(('user_id', '=', user_id.id))

        mrp_productions_ids = mrp_production_model.search(cr, uid, mrp_production_domain, context=context)

        if isinstance(mrp_productions_ids, (int, long)):
            mrp_productions_ids = [mrp_productions_ids]

        append_production = False
        # If another production order for the same sale order is present and not started, append to it
        #   but ONLY if the production order has a bom (production orders confirmed)
        if mrp_productions_ids:
            # Take first that has a bom
            for mrp_production in mrp_production_model.browse(cr, uid, mrp_productions_ids, context):
                bom_point = mrp_production.temp_bom_id
                bom_id = mrp_production.temp_bom_id.id
                if bom_point or bom_id:
                    append_production = True
                    break

        # From for above, mrp_production is the mrp order to which to append
        if append_production:
            mrp_production_id = mrp_production.id
            # Calculate qty according to UoM
            qty = uom_model._compute_qty(cr, uid, temp.product_uom.id, temp.product_qty, mrp_production.product_uom.id)

            newqty = mrp_production.product_qty + qty

            mrp_production_model.write(cr, uid, mrp_production_id,
                                       {'product_qty': newqty}, context)
        else:
            # Create new
            delay = max(product.sale_delay, product.produce_delay)
            # required_date = hasattr(temp.sale_order_id, 'minimum_planned_date') and temp.sale_order_id.minimum_planned_date or temp.sale_order_id.commitment_date
            dt = datetime.strptime(temp.order_requirement_line_id.delivery_date, DEFAULT_SERVER_DATE_FORMAT) - relativedelta(days=delay or 0.0)
            dt_s = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)

            mrp_production_values = mrp_production_model.product_id_change(cr, uid, [], product.id)['value']

            mrp_production_values.update({
                'date_planned': dt_s,
                'analytic_account_id': temp.sale_order_id.project_id and temp.sale_order_id.project_id.id or False,
                'product_id': product.id,
                'product_qty': temp.product_qty,
                'sale_id': temp.sale_order_id.id,
                # 'sale_name': temp.sale_order_id.name,
                # 'sale_ref': temp.sale_order_id.client_order_ref or '',
                'is_from_order_requirement': True,
                'temp_bom_id': temp.id,
                'level': temp.level,
                'notes': temp.order_requirement_line_id.order_requirement_id.internal_note or '',
            })
            if user_id:
                mrp_production_values.update(user_id=user_id.id)

            # Create manufacturing order
            mrp_production_id = mrp_production_model.create(cr, uid, mrp_production_values, context=context)

        if isinstance(mrp_production_id, (int, long)):
            mrp_production_ids = [mrp_production_id]
        else:
            mrp_production_ids = mrp_production_id

        mrp_production_model.action_compute(cr, uid, mrp_production_ids, context=context)
        self.write(cr, uid, temp.id, {'mrp_production_id': mrp_production_id}, context)
        return True

    def manufacture_or_purchase_rec(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        # is_split = user.company_id.split_mrp_production
        order_requirement_line_model = self.pool['order.requirement.line']
        for line in self.browse(cr, uid, ids, context):
            # test
            order_requirement_line_model._onchange_product_warning(line.product_id)
            order_requirement_line_model.onchange_partner_id(cr, uid, ids, line.supplier_id.id, context=None)

            is_split = line.order_requirement_line_id.split_mrp_production
            self._manufacture_or_purchase_rec(cr, uid, line, is_split, context)
        return True

    def _manufacture_or_purchase_rec(self, cr, uid, line, is_split, context=None):
        # todo test line.state != 'draft'
        if line.state != 'draft':
            return False
        if line.is_manufactured:
            # self._manufacture_bom(cr, uid, temp, context)
            # When splitting orders, create MRP order for every non-leaf bom (excluding level 0 already done)
            if is_split and line.level > 0:
                self._manufacture_bom(cr, uid, line, context)
            for child in line.bom_lines:
                self._manufacture_or_purchase_rec(cr, uid, child, is_split, context)
        else:
            self.pool['order.requirement.line']._purchase_bom(cr, uid, line, context)
        line.write({'state': 'done'})
        return True

    def action_add(self, cr, uid, ids, context):
        line = self.browse(cr, uid, ids, context)[0]
        context['line_id'] = line.order_requirement_line_id.id  # todo ask if ok
        dest_qty = line.product_qty + 1
        line_vals = self.onchange_temp_product_qty(cr, uid, ids, dest_qty, context)
        line_vals['product_qty'] = dest_qty
        self.write(cr, uid, line.id, line_vals, context)
        return True

    def action_remove(self, cr, uid, ids, context):
        line = self.browse(cr, uid, ids, context)[0]
        context['line_id'] = line.order_requirement_line_id.id  # todo ask if ok
        # on_change = "onchange_temp_product_qty(product_qty, context)" / >
        dest_qty = line.product_qty - 1
        if dest_qty > 0.0:
            line_vals = self.onchange_temp_product_qty(cr, uid, ids, dest_qty, context)
            line_vals['product_qty'] = dest_qty
            self.write(cr, uid, line.id, line_vals, context)
        return True

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
            values = parent[2]
            if TempMrpBom.check_parents(values, temp_mrp_bom_ids):
                return True
        return False

    def onchange_purchase_order_line_id(self, cr, uid, ids, purchase_order_line_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        ret = {
            'purchase_order_id': False
        }
        if purchase_order_line_id:
            order_id = self.pool['purchase.order.line'].read(cr, uid, purchase_order_line_id, ['order_id'], context=context, load='_obj')['order_id']
            ret['purchase_order_id'] = order_id
        return {'value': ret}

    def onchange_supplier_id(self, cr, uid, ids, supplier_id, product_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        ctx = context.copy()
        partner_obj = self.pool['res.partner']
        unit_price = 0
        ret = {}
        if ids and supplier_id:
            bom_line = self.browse(cr, uid, ids[0], ctx)
            if supplier_id:
                partner = partner_obj.browse(cr, uid, supplier_id, context=ctx)
                ctx['pricelist'] = partner.property_product_pricelist_purchase and partner.property_product_pricelist_purchase.id or False
                ctx['partner'] = partner.id
            unit_price = self.pool['product.product']._product_price(cr, uid, [bom_line.product_id.id], 'price', False, ctx)[bom_line.product_id.id]
            cost = self.pool['order.requirement.line']._get_cost_compute(bom_line.product_uom, bom_line.product_qty, unit_price)

            ret.update({
                'cost': cost,
                'partial_cost': unit_price
            })
            self.write(cr, uid, ids[0], ret, context)
        return {'value': ret}

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

        product = self.pool['product.product'].browse(cr, uid, new_product_id, context)
        warning = self.pool['order.requirement.line']._onchange_product_warning(product)
        return {'value': ret, 'warning': warning}

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

        split_mrp_production = bom_father.order_requirement_line_id.split_mrp_production
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
            for wc_use in father.temp_mrp_routing_lines:
                result2.append({
                    'name': wc_use.name,
                    'workcenter_id': wc_use.workcenter_id.id,
                    'sequence': wc_use.sequence,
                    'cycle': wc_use.cycle,
                    'hour': wc_use.hour
                })

        _explode_rec(bom_father, bom_factor)
        return result, result2

    def action_view_connected_document(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids, context)[0]
        if line.purchase_order_id:
            return line.action_view_purchase_order()
        elif line.mrp_production_id:
            return line.action_view_mrp_production()
        raise orm.except_orm(
            _('Error'),
            _('Missing document to open'))

    def action_view_purchase_order(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids, context)[0]

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'purchase', 'purchase_order_form')
        view_id = view and view[1] or False

        if not line.purchase_order_id:
            raise orm.except_orm(_('Error!'), _("Not exist a Purchase Order for this line"))

        return {
            'context': context,
            'type': 'ir.actions.act_window',
            'name': _('Purchase Order'),
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'res_id': line.purchase_order_id.id
        }

    def action_view_mrp_production(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids, context)[0]

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mrp', 'mrp_production_form_view')
        view_id = view and view[1] or False

        if not line.mrp_production_id:
            raise orm.except_orm(_('Error!'), _("Not exist a Manufacture Order for this line"))

        return {
            'context': context,
            'type': 'ir.actions.act_window',
            'name': _('Manufacturing Order'),
            'res_model': 'mrp.production',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'res_id': line.mrp_production_id.id
        }

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        group_obj = self.pool['res.groups']
        if not group_obj.user_in_group(cr, uid, uid, 'sale_order_requirement.open_order_requirement_by_line', context=context):
            if not isinstance(ids, (list, tuple)):
                ids = [ids]
            can_unlink_ids = self.search(cr, uid, [('id', 'in', ids), ('state', '=', 'draft')], context=context)
            if len(ids) != len(can_unlink_ids):
                raise orm.except_orm(
                    _("Bom Line"),
                    _("is not on 'draft' state"))
        res = super(TempMrpBom, self).unlink(cr, uid, ids, context)
        return res
