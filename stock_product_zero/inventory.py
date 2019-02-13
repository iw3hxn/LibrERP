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
from openerp.osv import fields, orm
import decimal_precision as dp
import one2many_sorted
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)



class stock_inventory(orm.Model):
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

        return super(stock_inventory, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order,
                                                 context=context, count=count)

    def unlink(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        move_to_unlink_ids = []
        for inventory in self.browse(cr, uid, ids, context):
            for move in inventory.move_ids:
                move_to_unlink_ids.append(move.id)
        res = super(stock_inventory, self).unlink(cr, uid, ids, context)
        if move_to_unlink_ids:
            ctx = context.copy()
            ctx['call_unlink'] = True
            self.pool['stock.move'].unlink(cr, uid, move_to_unlink_ids, ctx)
        return res


class stock_inventory_line(orm.Model):
    _inherit = "stock.inventory.line"

    _index_name = 'stock_inventory_line_prod_lot_id_index'

    def _auto_init(self, cr, context={}):
        super(stock_inventory_line, self)._auto_init(cr, context)
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s',
                   (self._index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON stock_inventory_line (prod_lot_id)'.format(name=self._index_name))
        return

    def get_color(self, cr, uid, ids, field_name, arg, context):
        start_time = datetime.datetime.now()
        value = {}
        for inventory_line in self.browse(cr, uid, ids, context):
            if inventory_line.product_qty_calc < 0:
                value[inventory_line.id] = 'fuchsia'
            elif inventory_line.product_qty_calc > inventory_line.product_qty:
                value[inventory_line.id] = 'red'
            elif inventory_line.product_qty_calc < inventory_line.product_qty:
                value[inventory_line.id] = 'orange'
            else:
                value[inventory_line.id] = 'black'

        end_time = datetime.datetime.now()
        duration_seconds = (end_time - start_time)
        duration = '{sec}'.format(sec=duration_seconds)
        _logger.info(u'Inventory Line get in {duration}'.format(duration=duration))
        return value

    _columns = {
            'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True,
                                         store=False),  # not possible to use store=true because function write value in sql
            'product_qty_calc': fields.float('Quantity Calculated', digits_compute=dp.get_precision('Product UoM'), readonly=False)
    }

    def on_change_product_id(self, cr, uid, ids, location_id, product, uom=False, to_date=False):
        res = super(stock_inventory_line, self).on_change_product_id(cr, uid, ids, location_id, product, uom, to_date)
        if 'product_qty' in res.get('value', []):
            res['value']['product_qty_calc'] = res['value']['product_qty']
        return res


class stock_fill_inventory(orm.TransientModel):
    _inherit = "stock.fill.inventory"
    _logger = logging.getLogger(__name__)
    _columns = {
        'display_with_zero_qty': fields.boolean('Display lines with zero')
    }

    def view_init(self, cr, uid, fields_list, context=None):
        super(stock_fill_inventory, self).view_init(cr, uid, fields_list, context=context)
        return True

    def fill_inventory(self, cr, uid, ids, context=None):
        # unfortunately not hook
        inventory_id = context['id']
        self._logger.debug('FGF fill inventory ids, context %s, %s' % (ids, context))
        display_with_zero_qty = None
        # FIXME - display_with_zero_qty access not possible
        # fill_inventory = self.browse(cr, uid, ids, context=context)
        # display_with_zero_qty = fill_inventory.display_with_zero_qty

        res_all = super(stock_fill_inventory, self).fill_inventory(cr, uid, ids, context)

        inventory_line_obj = self.pool.get('stock.inventory.line')
        if not display_with_zero_qty:
            ids_zero = inventory_line_obj.search(cr, uid,
                                                 [('inventory_id', '=', inventory_id), ('product_qty', '=', '0')])
            inventory_line_obj.unlink(cr, uid, ids_zero)
        ids_update = inventory_line_obj.search(cr, uid, [('inventory_id', '=', inventory_id)])
        ids2 = ','.join([str(id) for id in ids_update])
        if ids_update:
            cr.execute("""update stock_inventory_line
                         set product_qty_calc = product_qty
                       where id in (%s)""" % ids2)
        return res_all
