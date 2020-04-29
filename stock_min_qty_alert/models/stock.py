# -*- coding: utf-8 -*-
# © 2020 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _get_location_availability(self, cr, uid, ids, field, args, context):
        result = {}
        orderpoint_model = self.pool["stock.warehouse.orderpoint"]

        for move in self.browse(cr, uid, ids, context):
            if move.picking_id.state == 'draft':
                orderpoint_ids = orderpoint_model.search(cr, uid, [
                    ('location_id', '=', move.location_id.id)
                ])
                if orderpoint_ids:
                    orderpoint = orderpoint_model.browse(cr, uid, orderpoint_ids[0], context)
                    result[move.id] = (move.qty_available - move.product_qty) > orderpoint.product_min_qty
                else:
                    result[move.id] = move.qty_available > move.product_qty
            else:
                result[move.id] = True

        return result

    _columns = {
        'product_available': fields.function(_get_location_availability, string='Availability', method=True, type='boolean')
    }

    _defaults = {
        'product_available': True
    }
