# -*- coding: utf-8 -*-
from openerp.osv import orm, fields

import base64
import logging

from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


class StockComputeOutLine(orm.TransientModel):
    _name = 'stock.compute.out.line'
    _description = 'Stock Compute Out'

    _columns = {
        'wizard_id': fields.many2one('stock.compute.out'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'qty': fields.float(string="Qty", readonly=True),
        'qty_buy': fields.float(string="Qty Buy", readonly=True),
        'purchase_order': fields.char(string="Purchase Order"),
        'buy': fields.boolean(string="Buy")
    }

    def check_buy(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'buy': True}, context)

    def uncheck_buy(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'buy': False}, context)
