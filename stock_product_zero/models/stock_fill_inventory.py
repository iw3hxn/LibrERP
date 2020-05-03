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
import logging

from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class StockFillInventory(orm.TransientModel):
    _inherit = "stock.fill.inventory"
    _logger = logging.getLogger(__name__)
    _columns = {
        'display_with_zero_qty': fields.boolean('Display lines with zero')
    }

    def view_init(self, cr, uid, fields_list, context=None):
        super(StockFillInventory, self).view_init(cr, uid, fields_list, context=context)
        return True

    def fill_inventory(self, cr, uid, ids, context=None):
        # unfortunately not hook
        inventory_id = context['id']
        self._logger.debug('FGF fill inventory ids, context %s, %s' % (ids, context))
        # display_with_zero_qty = None
        # FIXME - display_with_zero_qty access not possible
        fill_inventory = self.browse(cr, uid, ids[0], context=context)
        display_with_zero_qty = fill_inventory.display_with_zero_qty

        res_all = super(StockFillInventory, self).fill_inventory(cr, uid, ids, context)

        inventory_line_obj = self.pool['stock.inventory.line']
        if not display_with_zero_qty:
            ids_zero = inventory_line_obj.search(cr, uid, [('inventory_id', '=', inventory_id), ('product_qty', '=', '0')], context=context)
            inventory_line_obj.unlink(cr, uid, ids_zero, context=context)
        ids_update = inventory_line_obj.search(cr, uid, [('inventory_id', '=', inventory_id)], context=context)
        ids2 = ','.join([str(id) for id in ids_update])
        if ids_update:
            cr.execute("""update stock_inventory_line
                         set product_qty_calc = product_qty
                       where id in (%s)""" % ids2)
        return res_all
