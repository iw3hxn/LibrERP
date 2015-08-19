# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
import decimal_precision as dp


class stock_partial_picking_line_split(orm.TransientModel):
    _name = "stock.partial.picking.line.split"
    _description = "Split into"
    _columns = {
        'quantity': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
    }
    _defaults = {
        'quantity': 0,
    }

    def split(self, cr, uid, data, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        rec_id = context and context.get('active_ids', False)
        move_obj = self.pool['stock.partial.picking.line']

        quantity = self.browse(cr, uid, data[0], context=context).quantity or 0.0
        for move in move_obj.browse(cr, uid, rec_id, context=context):
            quantity_rest = move.quantity - quantity
            #if move.tracking_id :
            #    raise osv.except_osv(_('Error!'),  _('The current move line is already assigned to a pack, please remove it first if you really want to change it ' \
            #                        'for this product: "%s" (id: %d)') % \
            #                        (move.product_id.name, move.product_id.id,))
            if quantity > move.quantity:
                raise orm.except_orm(_('Error!'), _('Total quantity after split exceeds the quantity to split '
                                                    'for this product: "%s" (id: %d)') %
                                     (move.product_id.name, move.product_id.id,))
            if quantity > 0:
                move_obj.write(cr, uid, [move.id], {
                    'quantity': quantity,
                    'product_uom': move.product_uom.id,
                })

            if quantity_rest > 0:
                quantity_rest = move.quantity - quantity

                if quantity != 0.0:
                    default_val = {
                        'quantity': quantity_rest,
                        'product_uom': move.product_uom.id
                    }

                    move_obj.copy(cr, uid, move.id, default_val, context=None)

        #return {'type': 'ir.actions.act_window_close'}
        return True
