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
from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class StockInventoryLine(orm.Model):
    _inherit = "stock.inventory.line"

    _index_name = 'stock_inventory_line_prod_lot_id_index'

    def _auto_init(self, cr, context={}):
        super(StockInventoryLine, self)._auto_init(cr, context)
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s',
                   (self._index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON stock_inventory_line (prod_lot_id)'.format(name=self._index_name))
        return

    def _get_product_value_hook(self, cr, uid, stock_inventory_line, context):
        if stock_inventory_line.product_id.is_kit:
            product_value = stock_inventory_line.product_id.cost_price
        else:
            product_value = stock_inventory_line.product_id.standard_price
        return product_value

    def _get_value(self, cr, uid, ids, field_name, arg, context):
        start_time = datetime.datetime.now()
        value = {}
        for line in self.browse(cr, uid, ids, context):
            row_color = 'black'
            if line.product_qty_calc < 0:
                row_color = 'fuchsia'
            elif line.product_qty_calc > line.product_qty:
                row_color = 'red'
            elif line.product_qty_calc < line.product_qty:
                row_color = 'orange'

            value[line.id] = {
                'row_color': row_color,
                'prefered_supplier_id': line.product_id.prefered_supplier and line.product_id.prefered_supplier.id or False,
                'qty_diff': line.product_qty - line.product_qty_calc,
            }

            product_value = self._get_product_value_hook(cr, uid, line, context)

            value[line.id].update({
                    'product_value': product_value,
                    'total_value': line.product_qty * product_value,
                    'total_value_computed': line.product_qty_calc * product_value
                })

        end_time = datetime.datetime.now()
        duration_seconds = (end_time - start_time)
        duration = '{sec}'.format(sec=duration_seconds)
        _logger.info(u'Inventory Line get in {duration}'.format(duration=duration))
        return value

    def _get_evaluation(self, cr, uid, ids, field_name, arg, context):
        start_time = datetime.datetime.now()
        value = {}
        for line in self.browse(cr, uid, ids, context):
            product_value = self._get_product_value_hook(cr, uid, line, context)
            value[line.id] = {
                    'product_value': product_value,
                    'total_value': line.product_qty * product_value,
                    'total_value_computed': line.product_qty_calc * product_value
                }

        end_time = datetime.datetime.now()
        duration_seconds = (end_time - start_time)
        duration = '{sec}'.format(sec=duration_seconds)
        _logger.info(u'Inventory Evaluation Line get in {duration}'.format(duration=duration))
        return value

    _columns = {
        'row_color': fields.function(_get_value, string='Row color', type='char', readonly=True, method=True, store=False, multi="_get_value"),
        'product_qty_calc': fields.float('Quantity Calculated', digits_compute=dp.get_precision('Product UoM'), readonly=False),
        'prefered_supplier_id': fields.function(_get_value, string="Default Supplier", type="many2one", relation="res.partner", multi="_get_value"),
        'qty_diff': fields.function(_get_value, string="Diff", type="float",  multi="_get_value"),
        'product_value':  fields.function(_get_value, string="Value", type="float", multi="_get_evaluation"),
        'total_value': fields.function(_get_value, string="Total Value counted", type="float",  multi="_get_evaluation"),
        'total_value_computed': fields.function(_get_value, string="Total Value computed", type="float",  multi="_get_evaluation"),
    }

    def on_change_product_id(self, cr, uid, ids, location_id, product, uom=False, to_date=False):
        res = super(StockInventoryLine, self).on_change_product_id(cr, uid, ids, location_id, product, uom, to_date)
        if 'product_qty' in res.get('value', []):
            res['value']['product_qty_calc'] = res['value']['product_qty']
        return res

