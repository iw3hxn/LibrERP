# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

import netsvc
import logging
from osv import osv
from tools.translate import _
_logger = logging.getLogger(__name__)
from openerp.osv import orm, fields


class StockMove(orm.Model):
    _inherit = 'stock.move'

    _index_name = 'stock_move_purchase_line_id_state_index'

    def _auto_init(self, cr, context={}):
        res = super(StockMove, self)._auto_init(cr, context)
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s', (self._index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON stock_move (purchase_line_id, state)'.format(name=self._index_name))
        return res

    def _force_production_order(self, cr, uid, stock_move_ids, context):
        user = self.pool['res.users'].browse(cr, uid, uid, context)

        if user.company_id.auto_production:
            mrp_production_obj = self.pool['mrp.production']
            order_requirement_line_obj = self.pool['order.requirement.line']
            wf_service = netsvc.LocalService("workflow")
            for stock_move in self.browse(cr, uid, stock_move_ids, context):
                for mrp_production in stock_move.production_order_ids:

                    if mrp_production and mrp_production.state != 'done':
                        wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_confirm', cr)
                        wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'force_production', cr)
                        wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_produce', cr)
                        mrp_production_obj.action_produce(cr, uid, mrp_production.id, mrp_production.product_qty,
                                                          'consume_produce', context=context)
            return True
        return False

    def _action_check_goods_ready_hook(self, cr, uid, stock_move_ids, context):
        res = super(StockMove, self)._action_check_goods_ready_hook(cr, uid, stock_move_ids, context)
        self._force_production_order(cr, uid, stock_move_ids, context)
        return res

    # from profilehooks import profile
    # @profile(immediate=True)
    def _get_connected_order_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for stock_move in self.browse(cr, uid, ids, context):
            order_name = ''
            order_ids = []
            if stock_move.purchase_line_id:
                for line in stock_move.purchase_line_id.temp_mrp_bom_ids:
                    if order_name:
                        order_name += ', '
                    order_name += line.name_get()[0][1]
                    order_ids.append(line.id)
            elif stock_move.sale_line_id and stock_move.sale_line_id.order_requirement_line_ids:
                for requirement_line in stock_move.sale_line_id.order_requirement_line_ids:
                    for line in requirement_line.temp_mrp_bom_ids:
                        if order_name:
                            order_name += ', '
                        order_name += line.name_get()[0][1]
                        order_ids.append(line.id)
            res[stock_move.id] = {
                'temp_mrp_bom_list': order_name,
                'temp_mrp_bom_ids': order_ids
            }
        return res

    def _line_ready(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, False)

        order_requirement_line_obj = self.pool['order.requirement.line']
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        stock_move_confirmed_ids = self.search(cr, uid, [('state', 'in', ['assigned', 'done']), ('id', 'in', ids)], context=context)
        for stock_id in stock_move_confirmed_ids:
            res[stock_id] = True

        stock_move_sale_ids = self.search(cr, uid, [('sale_id', '!=', False), ('id', 'in', ids), ('state', 'not in', ['assigned', 'done'])], context=context)

        for stock_move in self.read(cr, uid, stock_move_sale_ids, ['sale_line_id'], context=context):
            res[stock_move['id']] = False
            # sale_id = stock_move.sale_id and stock_move.sale_id.id or False
            sale_order_line_id = stock_move['sale_line_id'] and stock_move['sale_line_id'][0] or False
            if True:
                order_requirement_line_ids = order_requirement_line_obj.search(cr, uid, [('sale_order_line_id', '=', sale_order_line_id)], context=context)
                temp_mrp_bom_ids = temp_mrp_bom_obj.search(cr, uid, [('order_requirement_line_id', 'in', order_requirement_line_ids), ('mrp_production_id', '!=', False)], context=context)
                # if not temp_mrp_bom_ids:  # if not exist production order means that is a normal product
                #     if stock_move.state == 'assigned':
                #         res[stock_move.id] = True
                for temp_mrp_bom in temp_mrp_bom_obj.browse(cr, uid, temp_mrp_bom_ids, context):
                    res[stock_move['id']] = True
                    if temp_mrp_bom.mrp_production_id and temp_mrp_bom.mrp_production_id.state != 'done':
                        res[stock_move['id']] = False

        return res

    def _purchase_orders_approved(self, cr, uid, ids, name, args, context=None):
        # Get the order approved by order requirement line, from sale order id
        context = context or self.pool['res.users'].context_get(cr, uid)
        ordreqline_obj = self.pool['order.requirement.line']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            done = 0
            tot = 0
            try:
                ordreqline_ids = ordreqline_obj.search(cr, uid, [('sale_order_id', '=', line.sale_id.id),
                                                                 ('new_product_id', '=', line.product_id.id)],
                                                       context=context)
                # Maybe useless, but is generic, it supports eventually multiple lines
                for ordreqline in ordreqline_obj.browse(cr, uid, ordreqline_ids, context):
                    d, t = ordreqline_obj.get_purchase_orders_approved(ordreqline)
                    done += d
                    tot += t
                state_str = ''
                if tot > 0:
                    state_str = '%d/%d' % (done, tot)
            except Exception as e:
                _logger.error('_purchase_orders_approved ' + e.message)
                state_str = ''
            res[line.id] = state_str
        return res

    def _purchase_orders_state(self, cr, uid, ids, name, args, context=None):
        # Get the order state by order requirement line, from sale order id
        context = context or self.pool['res.users'].context_get(cr, uid)
        ordreqline_obj = self.pool['order.requirement.line']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            done = 0
            tot = 0
            try:
                ordreqline_ids = ordreqline_obj.search(cr, uid, [('sale_order_id', '=', line.sale_id.id),
                                                                 ('new_product_id', '=', line.product_id.id)],
                                                       context=context)
                # Maybe useless, but is generic, it supports eventually multiple lines
                for ordreqline in ordreqline_obj.browse(cr, uid, ordreqline_ids, context):
                    d, t = ordreqline_obj.get_purchase_orders_state(ordreqline)
                    done += d
                    tot += t
                state_str = ''
                if tot > 0:
                    state_str = '{0}/{1}'.format(done, tot)
            except Exception as e:
                _logger.error('_purchase_orders_state ' + e.message)
                state_str = ''
            res[line.id] = state_str

        return res

    def _purchase_orders(self, cr, uid, ids, name, args, context=None):
        # Get the order state by order requirement line, from sale order id
        context = context or self.pool['res.users'].context_get(cr, uid)
        ordreqline_obj = self.pool['order.requirement.line']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            state_str = ''
            purchase_orders_state = ''

            try:
                ordreqline_ids = ordreqline_obj.search(cr, uid, [('sale_order_line_id', '=', line.sale_line_id.id), ('new_product_id', '=', line.product_id.id)], context=context)

                # Maybe useless, but is generic, it supports eventually multiple lines
                ordreqlines = ordreqline_obj.browse(cr, uid, ordreqline_ids, context)

                done = 0
                tot = 0

                done_approved = 0
                tot_approved = 0

                for ordreqline in ordreqlines:
                    d, t = ordreqline_obj.get_purchase_orders_state(ordreqline)
                    done += d
                    tot += t

                    d_approved, t_approved = ordreqline_obj.get_purchase_orders_approved(ordreqline)
                    done_approved += d_approved
                    tot_approved += t_approved

                if tot > 0:
                    purchase_orders_state = '{0}/{1}'.format(done, tot)

                if tot_approved > 0:
                    state_str = '{0}/{1}'.format(done_approved, tot_approved)

            except Exception as e:
                _logger.error('_purchase_orders_state ' + e.message)
                purchase_orders_state = ''
                state_str = ''

            res[line.id] = {
                'purchase_orders_approved': state_str,
                'purchase_orders_state': purchase_orders_state
            }

        return res

    def _has_bom(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            try:
                has_bom = bool(move.product_id.bom_ids)
            except Exception as e:
                _logger.error(e)
                has_bom = False
            res[move.id] = has_bom
        return res

    def _get_production_order(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        order_requirement_line_obj = self.pool['order.requirement.line']

        for stock_move in self.browse(cr, uid, ids, context):
            mrp_production_ids = []
            sale_id = stock_move.sale_id and stock_move.sale_id.id or False
            sale_order_line_id = stock_move.sale_line_id and stock_move.sale_line_id.id or False
            done = 0
            tot = 0
            state_str = ''
            if sale_id and sale_order_line_id:
                order_requirement_line_ids = order_requirement_line_obj.search(cr, uid, [('sale_order_line_id', '=', sale_order_line_id)], context=context)
                for order_requirement_line in order_requirement_line_obj.browse(cr, uid, order_requirement_line_ids, context):
                    for temp in order_requirement_line.temp_mrp_bom_ids:
                        mrp_production = temp.mrp_production_id or False
                        if mrp_production:
                            tot += 1
                            mrp_production_ids.append(mrp_production.id)
                            if mrp_production.state == 'done':
                                done += 1
            if tot > 0:
                state_str = '{0}/{1}'.format(done, tot)

            res[stock_move.id] = {
                'production_order_ids': list(set(mrp_production_ids)),
                'production_order_state': state_str
            }
        return res

    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', ),
        'goods_ready': fields.function(_line_ready, string='Goods Ready', type='boolean', store=False),
        'temp_mrp_bom_ids': fields.function(_get_connected_order_ids, type='one2many', relation='temp.mrp.bom', method=True, string='Bom Structure',
                                             multi="connected_order"),
        'temp_mrp_bom_list': fields.function(_get_connected_order_ids, type='char', method=True, string='Sale Orders', multi="connected_order"),
        'purchase_orders_approved': fields.function(_purchase_orders, method=True, type='char', size=128, multi="purchase_orders",
                                                    string='Purch. orders approved', readonly=True),
        'purchase_orders_state': fields.function(_purchase_orders, method=True, type='char', size=128,  multi="purchase_orders",
                                                 string='Incoming Deliveries', readonly=True),
        'production_order_ids': fields.function(_get_production_order, type='one2many', relation='mrp.production', method=True, string='Production Orders', multi="production_order"),
        'production_order_state': fields.function(_get_production_order, type='char', size=128, method=True, string='Production Order', multi="production_order"),

        'product_bom_ids': fields.related(
            'sale_line_id', 'order_requirement_line_ids', 'temp_mrp_bom_ids', 'product_id',
            string='Product BOM', relation='product.product', type='many2one'),
        'has_bom': fields.function(_has_bom, method=True, type='boolean', string='Product has bom?', readonly=True),

    }

    def print_production_order(self, cr, uid, ids, context):
        order_requirement_line_obj = self.pool['order.requirement.line']
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']

        production_ids = []
        for stock_move in self.browse(cr, uid, ids, context):

            sale_id = stock_move.sale_id and stock_move.sale_id.id or False
            sale_order_line_id = stock_move.sale_line_id and stock_move.sale_line_id.id or False
            if sale_id and sale_order_line_id:
                order_requirement_line_ids = order_requirement_line_obj.search(cr, uid, [
                    ('sale_order_line_id', '=', sale_order_line_id)], context=context)
                temp_mrp_bom_ids = temp_mrp_bom_obj.search(cr, uid, [
                    ('order_requirement_line_id', 'in', order_requirement_line_ids),
                    ('mrp_production_id', '!=', False)], context=context)
                for temp_mrp_bom in temp_mrp_bom_obj.browse(cr, uid, temp_mrp_bom_ids, context):
                    if temp_mrp_bom.mrp_production_id:
                        production_ids.append(temp_mrp_bom.mrp_production_id.id)

        return self.pool['account.invoice'].print_report(cr, uid, production_ids, 'mrp.report_mrp_production_report', context)

    def print_bom_explode(self, cr, uid, ids, context):
        mrp_bom_obj = self.pool['mrp.bom']
        product_ids = []
        for stock_move in self.browse(cr, uid, ids, context):
            if stock_move.product_id:
                product_ids.append(stock_move.product_id.id)
        bom_ids = mrp_bom_obj.search(cr, uid, [('product_id', 'in', product_ids)], context=context)
        return self.pool['account.invoice'].print_report(cr, uid, bom_ids, 'mrp.report_bom_structure', context)

    def action_view_bom(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids, context)[0]

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mrp', 'mrp_bom_tree_view')
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Product BOM'),
            'res_model': 'mrp.bom',
            'view_type': 'tree',
            'view_mode': 'tree',
            'view_id': [view_id],
            'domain': [('product_id', '=', line.product_id.id),
                       ('bom_id', '=', False)],
            'res_id': False
        }

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if isinstance(ids, (int, long)):
            ids = [ids]
        new_ids = [i for i in ids if i]
        if 'state' in vals or 'product_id' in vals:
            self.pool['temp.mrp.bom'].stock_availability = {}
        return super(StockMove, self).write(cr, uid, new_ids, vals, context)

    def create(self, cr, uid, vals, context=None):
        self.pool['temp.mrp.bom'].stock_availability = {}
        return super(StockMove, self).create(cr, uid, vals, context)

    def remove_from_production(self, cr, uid, ids, context=None):
        context['call_unlink'] = True
        mrp_production_obj = self.pool['mrp.production']
        production = None

        try:
            picking_id = self.browse(cr, uid, ids[0], context).picking_id.id
            production_id = mrp_production_obj.search(cr, uid, [('picking_id', '=', picking_id)])[0]
            production = mrp_production_obj.browse(cr, uid, production_id, context)
        except:
            pass

        if production and production.state == 'done': #('picking_except', 'confirmed', 'ready'):
            raise osv.except_osv(_('UserError'), _('Production already finished'))
        try:
            self.unlink(cr, uid, ids, context)
        except:
            # If not found -> maybe already removed
            pass

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mrp', 'mrp_production_form_view')
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Manufacturing Orders'),
            'res_model': 'mrp.production',
            'view_mode': 'page',
            'view_id': [view_id],
            'target': 'current',
            'res_id': production_id,
        }

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(StockMove, self).default_get(cr, uid, fields, context)
        if context.get('edit_mrp_production', False):
            location_id = context.get('location_id', False)
            product_id = context.get('production_product_id', False)
            location_dest_id = False
            if product_id:
                location_dest_id = self.pool['product.product'].browse(cr, uid, product_id, context).product_tmpl_id.property_stock_production.id
            res['location_id'] = location_id
            res['location_dest_id'] = location_dest_id
        return res
