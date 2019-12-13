# -*- coding: utf-8 -*-
##############################################################################

#    Copyright (C) 2015-2019 Didotech srl
#    (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import decimal_precision as dp
from openerp.osv import orm, fields
from collections import defaultdict


class stock_move(orm.Model):
    _inherit = "stock.move"

    def _line_ready(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, False)
        move_assigned_ids = self.search(cr, uid, [('state', '=', 'assigned')], context=context)
        for move_id in move_assigned_ids:
            res[move_id] = True
        return res

    def _get_related_fields(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for move in self.read(cr, uid, ids, ['picking_id'], context):
            res[move['id']] = {
                'minimum_planned_date': False,
                'sale_id': False,
                'week_nbr': False,
                'shop_id': False
            }
            if move['picking_id']:
                picking = self.pool['stock.picking'].browse(cr, uid, move['picking_id'][0], context)
                res[move['id']]['week_nbr'] = picking.week_nbr
                if picking.sale_id:
                    res[move['id']].update({
                        'sale_id': picking.sale_id.id,
                        'minimum_planned_date': picking.sale_id.minimum_planned_date,
                        'shop_id': picking.sale_id.shop_id.id
                    })
        return res

    def _get_picking_sale(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        stock_picking_model = self.pool['stock.picking']
        stock_move_model = self.pool['stock.move']
        picking_ids = stock_picking_model.search(cr, uid, [('sale_id', 'in', ids)], context=context)
        move_ids = stock_move_model.search(cr, uid, [('picking_id', 'in', picking_ids)], context=context)
        return move_ids

    def _get_picking(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        stock_move_model = self.pool['stock.move']
        move_ids = stock_move_model.search(cr, uid, [('picking_id', 'in', ids)], context=context)
        return move_ids

    def _get_average_price(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = defaultdict(dict)
        stock_move_group_read_ids = []
        stock_move_group_obj = self.pool['stock.move.group']
        for move in self.read(cr, uid, ids, ['product_id', 'location_id'], context=context, load='_obj'):
            res[move['id']] = {
                'average_price': 0,
                'stock_move_group_id': False
            }
            product_id = move['product_id']
            location_id = move['location_id']
            stock_move_group_ids = stock_move_group_obj.search(cr, uid, [('product_id', '=', product_id), ('location_id', '=', location_id), ('move_line_id', '=', move['id'])], context=context)
            if stock_move_group_ids:
                res[move['id']]['stock_move_group_id'] = stock_move_group_ids[0]
                stock_move_group_read_ids.append(stock_move_group_ids[0])

        for move_group in stock_move_group_obj.browse(cr, uid, stock_move_group_read_ids, context=context):
            move_id = move_group.move_line_id.id
            average_price = move_group.average
            res[move_id]['average_price'] = average_price

        return dict(res)

    _columns = {
        'goods_ready': fields.function(_line_ready, string='Goods Ready', type='boolean', store=False),
        'shop_id': fields.function(_get_related_fields, type='many2one', relation='sale.shop', string='Shop', multi='related_fields', store={
                                                    'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['picking_id'], 20),
                                                    'stock.picking': (_get_picking, ['sale_id', 'move_lines'], 5000),
                                                    'sale.order': (_get_picking_sale, ['shop_id'], 8000),
                                                }),
        'minimum_planned_date': fields.function(_get_related_fields, type='date', string='Expected Date', multi='related_fields', store={
                                        'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['picking_id'], 20),
                                        'stock.picking': (_get_picking, ['sale_id', 'move_lines'], 5000),
                                        'sale.order': (_get_picking_sale, ['minimum_planned_date'], 8000),
                                        }),
        'sale_id': fields.function(_get_related_fields, relation='sale.order', type='many2one', string='Sale Order', multi='related_fields'),
        'week_nbr': fields.function(_get_related_fields, type='integer', string="Week Number", multi='related_fields'),
        'line_price_subtotal': fields.related('sale_line_id', 'price_subtotal', type='float', string='Line Amount (VAT Excluded)', digits_compute=dp.get_precision('Sale Price'),
                                       readonly=True, store=False, auto_join=True),
        'average_price': fields.function(_get_average_price, type='float', string="Average Price", digits_compute=dp.get_precision('Purchase Price'), multi='related_move_group'),
        'stock_move_group_id': fields.function(_get_average_price, type='many2one', relation='stock.move.group', string="Stock Move Group", multi='related_move_group'),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'internal_note': fields.text('Internal Note'),
    }

    def _default_journal_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        picking_type = context.get('picking_type', False)
        stock_journal_id = context.get('stock_journal_id', False)
        res = []
        if picking_type == 'out' and stock_journal_id:
            journal = self.pool['stock.journal'].browse(cr, uid, stock_journal_id, context)
            res = journal.warehouse_id and journal.warehouse_id.lot_stock_id and journal.warehouse_id.lot_stock_id.id or False
        if not res:
            res = super(stock_move, self)._default_location_source(cr, uid, context)
        return res

    def _default_journal_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        picking_type = context.get('picking_type', False)
        stock_journal_id = context.get('stock_journal_id', False)
        res = []
        if picking_type == 'out' and stock_journal_id:
            journal = self.pool['stock.journal'].browse(cr, uid, stock_journal_id, context)
            res = journal.lot_output_id and journal.lot_output_id.id or journal.warehouse_id and journal.warehouse_id.lot_output_id and journal.warehouse_id.lot_output_id.id or False
        if not res:
            res = super(stock_move, self)._default_location_destination(cr, uid, context)
        return res

    def _action_check_goods_ready_hook(self, cr, uid, ids, context):
        return True

    def action_check_goods_ready(self, cr, uid, move_ids, context):
        line = self.browse(cr, uid, move_ids, context)[0]
        return_vals = True
        line_vals = {'goods_ready': True}

        if line.product_id.track_outgoing and not line.prodlot_id:
            view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'stock', 'view_split_in_lots')
            view_id = view and view[1] or False
            # order_requirement_line_obj = self.pool[context['active_model']]
            # order_requirement_line = order_requirement_line_obj.browse(cr, uid, context['active_id'], context)
            # bom_childs = order_requirement_line.product_id.bom_ids[0].child_complete_ids
            # self.create_temp_mrp_boms(cr, uid, bom_childs, context)
            context_copy = context.copy()
            context_copy['active_id'] = line.id
            return_vals = {
                'type': 'ir.actions.act_window',
                'name': 'Product BOM',
                'res_model': 'stock.move.split',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [view_id],
                'target': 'new',
                'res_id': False,
                'context': context_copy,
            }

        else:
            line.write(line_vals)
            self.force_assign(cr, uid, [line.id], context)
            self._action_check_goods_ready_hook(cr, uid, [line.id], context)

        return return_vals

    _defaults = {
        'location_id': _default_journal_location_source,
        'location_dest_id': _default_journal_location_destination,
    }

    def action_view_order_board(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'stock_picking_extended', 'action_view_stock_picking')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        # compute the number of delivery orders to display
        pick_ids = []
        for move in self.browse(cr, uid, ids, context=context):
            pick_ids += [move.picking_id.id]

        view_id = False
        for view in result['views']:
            if view[1] == 'form':
                view_id = view[0]

        return {
            'name': result['name'],
            'view_type': 'page',
            'view_mode': 'page',
            'view_id': [view_id],
            'res_model': result['res_model'],
            'context': result['context'],
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'res_id': pick_ids and pick_ids[0] or False
        }
