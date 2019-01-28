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
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_move(orm.Model):
    _inherit = "stock.move"
           
    def _get_direction(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.location_id.usage == 'internal' and move.location_dest_id.usage in ['supplier', 'customer']:
                res[move.id] = '-'
            elif move.location_id.usage in ['supplier', 'customer'] and move.location_dest_id.usage == 'internal':
                res[move.id] = '+'
            elif move.location_id.usage in ['internal', 'transit'] and move.location_dest_id.usage in ['internal', 'transit']:
                res[move.id] = '='
            elif move.location_id.usage in ['inventory', 'procurement', 'production'] and move.location_dest_id.usage == 'internal':
                res[move.id] = '<>'
            else:
                res[move.id] = ''
        return res

    def _get_running_balance(self, cr, uid, ids, name, args, context):
        res = {}
        balance = {}

        location_ids = []
        complete_name = context.get('own_values', {}).get('self', '')
        if complete_name:
            location_ids = self.pool['stock.location'].search(cr, uid, ([('complete_name', 'ilike', complete_name)]), limit=1, context=context)
        if location_ids:
            location_id = location_ids[0]
        ordered_ids = self.search(cr, uid, ([('id', 'in', ids)]), order='date ASC', context=context)
        for line in self.browse(cr, uid, ordered_ids, context=context):
            line_balance = 0
            if line.state == 'done':
                if line.product_id.id not in balance:
                    if location_ids:
                        inv_date = datetime.strptime(line.date, DEFAULT_SERVER_DATETIME_FORMAT) - timedelta(1)
                        inventory_date = '{0}-{1}-{2} 23:59:59'.format(inv_date.year, inv_date.month, inv_date.day)
                        context_product = context.copy()
                        context_product.update(
                            {
                                'states': ('done',),
                                'what': ('in', 'out'),
                                'location': location_id,
                                'to_date': inventory_date,
                            })
                        balance[line.product_id.id] = self.pool['product.product'].browse(cr, uid, line.product_id.id, context=context_product).qty_available
                    else:
                        balance[line.product_id.id] = 0
                #
                # if line.direction == '+':
                #     balance[line.product_id.id] += line.product_qty
                # elif line.direction == '-':
                #     balance[line.product_id.id] += line.product_qty
                if location_ids:
                    if line.location_dest_id.id == location_id:
                        balance[line.product_id.id] += line.product_qty
                    elif line.location_id.id == location_id:
                        balance[line.product_id.id] -= line.product_qty

                line_balance = balance[line.product_id.id]
            res[line.id] = line_balance
        return res

    def _get_origin_id(self, cr, uid, res_model, origin, context):
        order_obj = self.pool.get(res_model)
        order_id = False
        if order_obj:
            order_id = order_obj.search(cr, uid, [('name', '=', origin.split(':')[0])], limit=1, context=context)
        return order_id

    def _get_origin_date(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            origin = move.origin or ''
            res[move.id] = False
            for res_model in ['pos.order', 'sale.order', 'purchase.order']:
                order_id = self._get_origin_id(cr, uid, res_model, origin, context)
                if order_id:
                    res[move.id] = self.pool[res_model].browse(cr, uid, order_id[0]).date_order
                    break
        return res

    #from profilehooks import profile
    #@profile(immediate=True)
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """

        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        # # if line.order_id:
        # #     context['warehouse'] = self.order_id.shop_id.warehouse_id.id
        # location_group = []
        # for move in self.browse(cr, uid, ids, context):
        #     if move.location_id.id not in location_group:
        #         location_group[move.location_id.id] = [move.product_id.id]
        #     else:
        #         if move.product_id.id not in location_group[move.location_id.id]:
        #             location_group[move.location_id.id].append([move.product_id.id])
        # qty_availables = []
        # for location_id in location_group:
        #     c = context.copy()
        #     c.update({'location': location_id})
        #     qty_availables.append(self.pool['product.product']._product_available(cr, uid, location_group[location_id], field_names=['qty_available'], context=c))

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

        context = context or self.pool['res.users'].context_get(cr, uid)
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
            ctx = context.copy()
            doc_id = move.picking_id.id

            if not doc_id:
                return {}
        else:
            return {}

        ctx.update({'default_type': 'out', 'contact_display': 'partner'})
        # Open up the picking's form
        return {
            'name': name,
            'view_type': 'page',
            'view_mode': 'page',
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
                'view_type': 'page',
                'view_mode': 'page',
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

        context = context or self.pool['res.users'].context_get(cr, uid)
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
        stock_move_ids = []
        for order in self.pool['sale.order'].browse(cr, uid, ids, context=context):
            if order.origin:
                stock_move_ids = self.pool['stock.move'].search(cr, uid, [('origin', 'like', order.origin)], limit=1, context=context)
        return stock_move_ids

    def _get_purchase_order(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        stock_move_ids = []
        for order in self.pool['purchase.order'].browse(cr, uid, ids, context=context):
            if order.origin:
                stock_move_ids = self.pool['stock.move'].search(cr, uid, [('origin', 'like', order.origin)], limit=1, context=context)
        return stock_move_ids

    def _get_stock_location(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        stock_move_ids = self.pool['stock.move'].search(cr, uid, ['|', ('location_id', 'in', ids), ('location_dest_id', 'in', ids)], context=context)
        for move_id in stock_move_ids:
            result[move_id] = True
        return result.keys()
    
    _columns = {
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'direction': fields.function(_get_direction, method=True, type='char', string='Dir', readonly=True, store={
            'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['location_id', 'location_dest_id'], 20),
            'stock.location': (_get_stock_location, ['usage'], 20),
        }),
        'origin_date': fields.function(_get_origin_date, method=True, type='date', string='Origin Date', readonly=True,
                                       store=False),
        # 'origin_date': fields.function(_get_origin_date, method=True, type='date', string='Origin Date', readonly=True, store={
        #     'sale.order': (_get_sale_order, ['date_order'], 20),
        #     'purchase.order': (_get_purchase_order, ['date_order'], 20),
        # }),
        'sell_price': fields.related('sale_line_id', 'price_unit', type='float', relation='sale.order.line', string='Sell Price Unit', readonly=True, digits_compute= dp.get_precision('Sale Price')),
        'qty_available': fields.function(_product_available, multi='qty_available',
                                         type='float', digits_compute=dp.get_precision('Product UoM'),
                                         string='Quantity On Hand'),
        'default_code': fields.related('product_id', 'default_code',  type='char', string='Product Reference'),
        'running_balance': fields.function(_get_running_balance, method=True, string="Running Balance"),
    }

    def write(self, cr, uid, ids, values, context=None):  # check if when change unit of sale is the same category of product
        context = context or self.pool['res.users'].context_get(cr, uid)
        if values.get('product_uos', False) and not values.get('product_uom', False):
            to_unit = self.pool['product.uom'].browse(cr, uid, values.get('product_uos'), context)
            for move in self.browse(cr, uid, ids, context):
                if move.product_uos and move.product_uos.category_id.id != to_unit.category_id.id:
                    raise orm.except_orm(_('Error !'),
                                         _('Conversion from Product UoM %s to Default UoM %s is not possible as they both belong to different Category!.') % (move.product_uos.category_id.name, to_unit.category_id.name))
        return super(stock_move, self).write(cr, uid, ids, values, context)
    
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_order = order
        for domain in args:
            if domain[0] == 'date' and domain[1] == '>=':
                new_order = 'date ASC'
        res = super(stock_move, self).search(cr, uid, args, offset=offset, limit=limit, order=new_order, context=context, count=count)
        return res
