# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2013-2014 Didotech srl (info at didotech.com)
#                          All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import orm, fields


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _action_explode(self, cr, uid, move, context=None):
        """ Explodes pickings.
        @param move: Stock moves
        @return: True
        """
        move_obj = self.pool['stock.move']
        processed_ids = [move.id]
        if move.sale_line_id and move.sale_line_id._columns.get('with_bom', False) and move.sale_line_id.with_bom:
            if move.sale_line_id.product_id.bom_lines and move.sale_line_id.product_id.bom_lines[0].type == 'normal':
                return processed_ids
            factor = move.product_qty
            state = 'confirmed'
            if move.state == 'assigned':
                state = 'assigned'
            if move.picking_id.type == 'in':
                location_dest_id = move.picking_id.partner_id.property_stock_customer.id
            elif move.picking_id.type == 'out':
                location_dest_id = move.picking_id.partner_id.property_stock_customer.id

            for line in move.sale_line_id.mrp_bom:
                if line.product_id.type != 'service':
                    valdef = {
                        'picking_id': move.picking_id.id,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'product_qty': line.product_uom_qty * factor,
                        'product_uos': line.product_uom.id,
                        'product_uos_qty': line.product_uom_qty * factor,
                        'move_dest_id': move.id,
                        'state': state,
                        'name': line.product_id.name,
                        'price_unit': line.price_unit,
                        'sell_price': 0,
                        'note': line.name,
                        'move_history_ids': [(6, 0, [move.id])],
                        'move_history_ids2': [(6, 0, [])],
                        'procurements': [],
                        'location_dest_id': location_dest_id,
                    }
                    mid = move_obj.copy(cr, uid, move.id, default=valdef)
                    processed_ids.append(mid)
                move_obj.write(cr, uid, [move.id], {
                    'location_dest_id': move.location_id.id,  # dummy move for the kit
                    'auto_validate': True,
                    'picking_id': False,
                    'state': 'confirmed'
                })

        return processed_ids
