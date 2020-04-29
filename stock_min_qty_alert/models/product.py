# -*- coding: utf-8 -*-
# © 2020 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def _get_location_min_qty(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for product in self.browse(cr, uid, ids, context):
            field = []
            for location in product.orderpoint_ids:
                field.append("{}: {} {}".format(
                    location.location_id.name, location.product_min_qty, location.product_uom.name))

            result[product.id] = ','.join(field)

        return result

    _columns = {
        'location_min_qty': fields.function(_get_location_min_qty, string='Location Min Qty', method=True, type='text')
    }
