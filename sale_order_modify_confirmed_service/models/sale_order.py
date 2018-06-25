# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class sale_order(orm.Model):

    _inherit = 'sale.order'

    def _has_services(self, cr, uid, ids, field_name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}

        for order in self.browse(cr, uid, ids, context):
            lines_services = True
            for l in order.order_line:
                if l.product_id.type == 'service':
                    lines_services = True
                    break
            result[order.id] = lines_services
        return result

    _columns = {
        'has_services': fields.function(_has_services, type="boolean", string="Has Services")
    }
