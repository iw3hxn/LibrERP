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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class stock_move(orm.Model):
    _inherit = "stock.move"
           
    def _get_direction(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = {}
        for move in self.browse(cr, uid, ids, context=context):

            if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':
                res[move.id] = '-'
            elif move.location_id.usage in ['supplier', 'customer'] and move.location_dest_id.usage == 'internal':
                res[move.id] = '+'
            elif move.location_id.usage in ['internal', 'transit'] and move.location_dest_id.usage in ['internal', 'transit']:
                res[move.id] = '='
            elif move.location_id.usage in ['inventory', 'procurement', 'production'] and move.location_dest_id.usage == 'internal':
                res[move.id] = '<>'
            else:
                res[move.id] = []

        return res
    
    _columns = {
        'direction': fields.function(_get_direction, method=True, type="char", string='Dir', readonly=True),
        'sell_price': fields.related('sale_line_id', 'price_unit', type='float', relation='sale.order.line', string='Sell Price Unit', readonly=True)
    }

    def write(self, cr, uid, ids, values, context=None):  # check if when change unit of sale is the same category of product
        if values.get('product_uos', False):
            to_unit = self.pool['product.uom'].browse(cr, uid, values.get('product_uos'), context)
            for move in self.browse(cr, uid, ids, context):
                if move.product_uos.category_id.id != to_unit.category_id.id:
                    raise orm.except_orm(_('Error !'),
                                         _('Conversion from Product UoM %s to Default UoM %s is not possible as they both belong to different Category!.') % (move.product_uos.category_id.name, to_unit.category_id.name))
        return super(stock_move, self).write(cr, uid, ids, values, context)
    

