# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
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

from osv import osv, fields
from tools import ustr
from tools.translate import _


class stock_move(osv.osv):
    _inherit = "stock.move"
           
    def _get_direction(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for move in self.browse(cr, uid, ids):
            #import pdb; pdb.set_trace()
            if move.picking_id:
                if move.picking_id.type == 'in':
                    res[move.id] = '+'
                elif move.picking_id.type == 'out':
                    res[move.id] = '-'
                else:
                    res[move.id] = '='
            else:
                res[move.id] = []
        return res
    
    _columns = {
        'direction': fields.function(_get_direction, method=True, type="char", string='Dir', readonly=True),
        'sell_price': fields.related('sale_line_id', 'price_unit', type='float', relation='sale.order.line', string='Sell Price Unit', readonly=True)
    }
    

    

