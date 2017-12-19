# -*- coding: utf-8 -*-
##############################################################################

#    Copyright (C) 2015 Didotech srl
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

# import decimal_precision as dp

from openerp.osv import orm, fields


class stock_move(orm.Model):
    _inherit = "stock.move"

    def _line_ready(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            res[move.id] = False
            if move.state == 'done':
                res[move.id] = True
        return res

    _columns = {
        'goods_ready': fields.function(_line_ready, string='Goods Ready', type='boolean', store=False
        # {
        #         'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['state'], 500),
        # }
        ),
        'sale_id': fields.related('picking_id', 'sale_id', relation='sale.order', type='many2one', string='Sale Order')
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
            self.action_done(cr, uid, [line.id], context)

        return return_vals

    _defaults = {
        'location_id': _default_journal_location_source,
        'location_dest_id': _default_journal_location_destination,
    }
