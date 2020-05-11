# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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
import datetime
import logging

import decimal_precision as dp
import one2many_sorted
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class StockInventory(orm.Model):
    _inherit = "stock.inventory"

    def _total_account(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for inventory in self.browse(cr, uid, ids, context=context):
            res[inventory.id] = {
                'total_count': 0.0,
                'total_qty_calc': 0.0,
            }
            inventory_line_ids = self.pool['stock.inventory.line'].search(cr, uid, [('inventory_id', '=', inventory.id)], context=context)

            if inventory_line_ids:
                cr.execute("""
                    SELECT COALESCE(SUM(product_qty))
                    FROM stock_inventory_line
                    WHERE id IN ({inventory_line_ids})
                """.format(inventory_line_ids=', '.join([str(line_id) for line_id in inventory_line_ids])))
                total_count = cr.fetchone()[0] or 0.0
                res[inventory.id]['total_count'] = total_count

                cr.execute("""
                    SELECT COALESCE(SUM(product_qty_calc))
                    FROM stock_inventory_line
                    WHERE id IN ({inventory_line_ids})
                """.format(inventory_line_ids=', '.join([str(line_id) for line_id in inventory_line_ids])))
                total_qty_calc = cr.fetchone()[0] or 0.0
                res[inventory.id]['total_qty_calc'] = total_qty_calc

        return res

    def _get_inventory(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for line in self.pool['stock.inventory.line'].browse(cr, uid, ids, context=context):
            if line.inventory_id:
                result[line.inventory_id.id] = True
        return result.keys()

    def _get_inventory_years(self, cr, uid, fields, context=None):
        result = []
        first_inventory_id = self.search(cr, uid, [('date', '!=', False)], order='date asc', limit=1, context=context)
        if first_inventory_id:
            first_inventory = self.browse(cr, uid, first_inventory_id[0], context)
            first_year = datetime.datetime.strptime(first_inventory.date, DEFAULT_SERVER_DATETIME_FORMAT).year
        else:
            first_year = datetime.date.today().year

        for year in range(int(first_year), int(datetime.date.today().year) + 1):
            result.append((str(year), str(year)))
        return result

    def _get_inventory_year(self, cr, uid, ids, field_name, arg, context):
        inventories = self.browse(cr, uid, ids, context)

        result = {}
        for inventory in inventories:
            if inventory.date:
                result[inventory.id] = datetime.datetime.strptime(inventory.date,
                                                                      DEFAULT_SERVER_DATETIME_FORMAT).year
            else:
                result[inventory.id] = False
        return result

    _columns = {
        # 'inventory_line_id': fields.one2many('stock.inventory.line', 'inventory_id', 'Inventories', states={'done': [('readonly', True)]}),
        'year': fields.function(_get_inventory_year, 'Year', type='selection', selection=_get_inventory_years,
                                method=True, help="Select year"),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),

        'product_id': fields.related('inventory_line_id', 'product_id', type='many2one', relation='product.product',
                                     string='Product'),
        'inventory_line_id': one2many_sorted.one2many_sorted
        ('stock.inventory.line'
         , 'inventory_id'
         , 'Inventories'
         , states={'done': [('readonly', True)]}
         , order='product_id.name'),
        'inventory_line_loc_id': one2many_sorted.one2many_sorted
        ('stock.inventory.line'
         , 'inventory_id'
         , 'Inventories'
         , states={'done': [('readonly', True)]}
         , order='location_id.name, product_id.name'),

        'move_ids': one2many_sorted.many2many_sorted('stock.move', 'stock_inventory_move_rel', 'inventory_id',
                                                     'move_id', 'Created Moves',
                                                     order='product_id.name, prodlot_id.prefix, prodlot_id.name'),
        'total_count': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'),
                                       multi='sums', string="Total Count", store={
                'stock.inventory.line': (_get_inventory, ['product_qty'], 60),
            }, ),
        'total_qty_calc': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'),
                                       multi='sums', string="Total Calculated", store={
                'stock.inventory.line': (_get_inventory, ['product_qty_calc'], 40),
            }, ),
        'user_id': fields.many2one('res.users', 'User'),
    }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
    }

    _order = 'date desc'

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_args = []
        for arg in args:
            if arg[0] == 'year':
                new_args.append(('date', '>=', '{year}-01-01'.format(year=arg[2])))
                new_args.append(('date', '<=', '{year}-12-31'.format(year=arg[2])))
            else:
                new_args.append(arg)

        return super(StockInventory, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order,
                                                 context=context, count=count)

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        move_to_unlink_ids = []
        for inventory in self.browse(cr, uid, ids, context):
            for move in inventory.move_ids:
                move_to_unlink_ids.append(move.id)
        if move_to_unlink_ids:
            ctx = context.copy()
            ctx['call_unlink'] = True
            self.pool['stock.move'].unlink(cr, uid, move_to_unlink_ids, ctx)
        res = super(StockInventory, self).unlink(cr, uid, ids, context)
        return res

    def action_cancel_draft(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        move_to_unlink_ids = []
        for inventory in self.browse(cr, uid, ids, context):
            for move in inventory.move_ids:
                move_to_unlink_ids.append(move.id)
        if move_to_unlink_ids:
            ctx = context.copy()
            ctx['call_unlink'] = True
            self.pool['stock.move'].unlink(cr, uid, move_to_unlink_ids, ctx)
        res = super(StockInventory, self).action_cancel_draft(cr, uid, ids, context)
        return res

    def evaluation_inventory(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        stock_move_obj = self.pool['stock.move']
        to_currency = self.pool['res.users'].browse(cr, uid, uid, context).company_id.currency_id.id

        for inventory in self.browse(cr, uid, ids, context):
            ctx = {
                'date': inventory.date
            }
            for move in inventory.move_ids:
                prefered_supplier_id = move.product_id.prefered_supplier or False
                if not prefered_supplier_id:
                    _logger.error("Product {} without Supplier".format(move.product_id.name_get()[0][1]))
                    continue
                pricelist = prefered_supplier_id.property_product_pricelist_purchase
                if not pricelist:
                    continue
                try:
                    price = self.pool['product.pricelist'].price_get(cr, uid, [pricelist.id], move.product_id.id, 1,
                                                             prefered_supplier_id.id, context=ctx)[pricelist.id] or False
                except Exception as e:
                    price = self.pool['product.pricelist'].price_get(cr, uid, [pricelist.id], move.product_id.id, 1,
                                                                     prefered_supplier_id.id, context=context)[pricelist.id] or False
                if not price:
                    _logger.error("Product {} without Price".format(move.product_id.name_get()[0][1]))
                    continue
                from_currency = pricelist.currency_id.id

                price_subtotal = self.pool['res.currency'].compute(
                            cr, uid, round=False,
                            from_currency_id=from_currency,
                            to_currency_id=to_currency,
                            from_amount=price,
                            context=context
                        )
                price_unit = price_subtotal
                move.write({
                    'price_unit': price_subtotal
                })
