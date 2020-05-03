# -*- coding: utf-8 -*-

import logging

from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class StockInventoryLine(orm.Model):
    _inherit = "stock.inventory.line"

    def _get_product_value_hook(self, cr, uid, stock_inventory_line, context):
        res = super(StockInventoryLine, self)._get_product_value_hook(cr, uid, stock_inventory_line, context)
        if stock_inventory_line.inventory_id.evaluation_mode == 'average':
            location_id = stock_inventory_line.location_id.id
            product_id = stock_inventory_line.product_id.id
            data = stock_inventory_line.inventory_id.date[0:10]

            cr.execute("SELECT average FROM stock_move_group WHERE product_id = {} and location_id = {} and real_date <= '{}' ORDER BY real_date desc".format(product_id, location_id, data))
            res2 = cr.fetchone()
            if res2 and res2[0]:
                res = res2[0]
        return res
