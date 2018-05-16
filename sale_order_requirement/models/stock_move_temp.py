# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

import decimal_precision as dp
from osv import fields, orm
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class mrp_production_temp(orm.TransientModel):

    _name = 'stock.move.temp'

    _columns = {
        'wizard_id': fields.many2one('mrp.production.wizard'),
        'is_consumed': fields.boolean('Consumed Products'),
        'production_id': fields.many2one('mrp.production', 'Production Order generating'),
        'orig_stock_move_id': fields.many2one('stock.move', 'Original Stock Move (To be Consumed or Consumed)'),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM'), required=True),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
        'location_id': fields.many2one('stock.location', 'Source Location', select=True,states={'done': [('readonly', True)]}, help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations."),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', states={'done': [('readonly', True)]}, select=True, help="Location where the system will stock the finished products."),
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot'),
        'state': fields.char('State')
    }

    _defaults = {
        # Default is "to be consumed"
        'is_consumed': False,
        'orig_stock_move_id': False
    }

