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
import decimal_precision as dp


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

    def _get_origin_id(self, cr, uid, res_model, origin, context):
        sale_order_obj = self.pool.get(res_model)
        sale_order_id = False
        if sale_order_obj:
            sale_order_id = sale_order_obj.search(cr, uid, [('name', '=', origin.split(':')[0])], limit=1,
                                                  context=context)
        return sale_order_id

    def _get_origin_date(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            origin = move.origin or ''

            # SALE ORDER
            res_model = 'sale.order'
            sale_order_id = self._get_origin_id(cr, uid, res_model, origin, context)
            if sale_order_id:
                res[move.id] = self.pool[res_model].browse(cr, uid, sale_order_id[0]).date_order
            else:
                # PURCHASE ORDER
                res_model = 'purchase.order'
                purchase_order_id = self._get_origin_id(cr, uid, res_model, origin, context)
                if purchase_order_id:
                    res[move.id] = self.pool[res_model].browse(cr, uid, purchase_order_id[0]).date_order
                else:
                    res[move.id] = False
        return res

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """

        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        res = {}
        # if line.order_id:
        #     context['warehouse'] = self.order_id.shop_id.warehouse_id.id

        for move in self.browse(cr, uid, ids, context):
            c = context.copy()
            c.update({'location': move.location_id.id})
            qty_available = move.product_id._product_available(field_names=['qty_available'], context=c)[move.product_id.id]['qty_available']
            res[move.id] = {
                'qty_available': qty_available or 0.0,
            }
        return res

    def picking_open(self, cr, uid, ids, context=None):
        """
        @description  Open document (invoice or payment) related to the
                      unapplied payment or outstanding balance on this line
        """

        if not context:
            context = {}
        active_id = context.get('active_id')
        models = self.pool['ir.model.data']
        # Get this line's invoice id
        move = self.browse(cr, uid, ids[0], context)
        # if this is an unapplied payment(all unapplied payments hard-coded to -999),
        # get the referenced voucher
        if move.picking_id:
            if move.picking_id.type == 'in':
                view = models.get_object_reference(cr, uid, 'stock', 'view_picking_in_form')
            else:
                view = models.get_object_reference(cr, uid, 'stock', 'view_picking_out_form')

            view_id = view and view[1] or False
            name = _('Picking')
            res_model = 'stock.picking'
            ctx = "{}"
            doc_id = move.picking_id.id

            if not doc_id:
                return {}
        else:
            return {}

        # Open up the picking's form
        return {
            'name': name,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'res_model': res_model,
            'context': ctx,
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'res_id': doc_id,
        }

    def origin_open(self, cr, uid, ids, context=None):

        def return_value():
            return {
                'name': name,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [view_id],
                'res_model': res_model,
                'context': ctx,
                'type': 'ir.actions.act_window',
                'nodestroy': False,
                'target': 'current',
                'res_id': doc_id,
            }

        """
        @description  Open document (invoice or payment) related to the
                      unapplied payment or outstanding balance on this line
        """

        if not context:
            context = {}
        active_id = context.get('active_id')
        models = self.pool['ir.model.data']
        # Get this line's invoice id
        move = self.browse(cr, uid, ids[0], context)
        name = False
        origin = move.origin or ''

        # search SALE ORDER
        res_model = 'sale.order'
        sale_order_id = self._get_origin_id(cr, uid, res_model, origin, context)

        if sale_order_id:
            view = models.get_object_reference(cr, uid, 'sale', 'view_order_form')
            view_id = view and view[1] or False
            name = _('Sale Order')
            ctx = "{}"
            doc_id = sale_order_id[0]
            return return_value()

        # search PURCHASE ORDER
        res_model = 'purchase.order'
        purchase_order_id = self._get_origin_id(cr, uid, res_model, origin, context)
        if purchase_order_id:
            view = models.get_object_reference(cr, uid, 'purchase', 'purchase_order_form')
            view_id = view and view[1] or False
            name = _('Purchase Order')
            ctx = "{}"
            doc_id = purchase_order_id[0]
            return return_value()

        # search POS ORDER
        res_model = 'pos.order'
        pos_order_id = self._get_origin_id(cr, uid, res_model, origin, context)
        if pos_order_id:
            view = models.get_object_reference(cr, uid, 'point_of_sale', 'view_pos_pos_form')
            view_id = view and view[1] or False
            name = _('Pos Order')
            ctx = "{}"
            doc_id = pos_order_id[0]
            return return_value()

        return {}

    def _get_sale_order(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for order in self.pool['sale.order'].browse(cr, uid, ids, context=context):
            if order.origin:
                stock_move_ids = self.pool['stock.move'].search(cr, uid, [('origin', 'like', order.origin)], limit=1, context=context)
                for move_id in stock_move_ids:
                    result[move_id] = True
        return result.keys()

    def _get_purchase_order(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for order in self.pool['purchase.order'].browse(cr, uid, ids, context=context):
            if order.origin:
                stock_move_ids = self.pool['stock.move'].search(cr, uid, [('origin', 'like', order.origin)], limit=1, context=context)
                for move_id in stock_move_ids:
                    result[move_id] = True
        return result.keys()
    
    _columns = {
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'direction': fields.function(_get_direction, method=True, type='char', string='Dir', readonly=True, store={
            'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['location_id', 'location_dest_id'], 20)
        }),
        'origin_date': fields.function(_get_origin_date, method=True, type='date', string='Origin Date', readonly=True, store=False),
        'sell_price': fields.related('sale_line_id', 'price_unit', type='float', relation='sale.order.line', string='Sell Price Unit', readonly=True),
        'qty_available': fields.function(_product_available, multi='qty_available',
                                         type='float', digits_compute=dp.get_precision('Product UoM'),
                                         string='Quantity On Hand'),
    }

    def write(self, cr, uid, ids, values, context=None):  # check if when change unit of sale is the same category of product
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        if values.get('product_uos', False):
            to_unit = self.pool['product.uom'].browse(cr, uid, values.get('product_uos'), context)
            for move in self.browse(cr, uid, ids, context):
                if move.product_uos.category_id.id != to_unit.category_id.id:
                    raise orm.except_orm(_('Error !'),
                                         _('Conversion from Product UoM %s to Default UoM %s is not possible as they both belong to different Category!.') % (move.product_uos.category_id.name, to_unit.category_id.name))
        return super(stock_move, self).write(cr, uid, ids, values, context)
    

