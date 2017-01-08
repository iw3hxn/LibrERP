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
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)



class stock_inventory(orm.Model):
    _inherit = "stock.inventory"
    _columns = {
        # 'inventory_line_id': fields.one2many('stock.inventory.line', 'inventory_id', 'Inventories', states={'done': [('readonly', True)]}),
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
                                                     order='product_id.name, prodlot_id.prefix, prodlot_id.name')
    }
    _order = 'date desc'


class stock_inventory_line(orm.Model):
    _inherit = "stock.inventory.line"

    def get_color(self, cr, uid, ids, field_name, arg, context):
        start_time = datetime.now()
        value = {}
        for inventory_line in self.browse(cr, uid, ids, context):
            if inventory_line.product_qty_calc != inventory_line.product_qty:
                value[inventory_line.id] = 'red'
            elif inventory_line.product_qty_calc < 0:
                value[inventory_line.id] = 'fuchsia'
            else:
                value[inventory_line.id] = 'black'

        end_time = datetime.now()
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
