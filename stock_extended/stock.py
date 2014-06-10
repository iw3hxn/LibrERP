# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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
##############################################################################

from openerp.osv import orm


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def write(self, cr, uid, ids, values, context=None):
        if values.get('date', False):
            move_lines = []
            processed_line_ids = []
            for picking in self.browse(cr, uid, ids, context):
                if values.get('move_lines', False):
                    for line in values['move_lines']:
                        line[2]['date'] = values['date']
                        if not line[0] == 0:
                            processed_line_ids.append(line[1])

                for stock_move in picking.move_lines:
                    if stock_move.id not in processed_line_ids:
                        move_lines.append([1, stock_move.id, {'date': values['date']}])

            if move_lines:
                values['move_lines'] = values.get('move_lines', []) + move_lines

        return super(stock_picking, self).write(cr, uid, ids, values, context)
