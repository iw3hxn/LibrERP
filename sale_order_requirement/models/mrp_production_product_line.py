# -*- coding: utf-8 -*-
# © Didotech srl (www.didotech.com)

from osv import fields, orm
from tools.translate import _


class mrp_production_product_line(orm.Model):

    _inherit = "mrp.production.product.line"

    def onchange_product_id(self, cr, uid, ids, product_id, product_qty=1, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result_dict = {}

        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context)
            result_dict.update({
                'name': product.name,
                'product_uom': product.uom_id and product.uom_id.id or False,
                'product_qty': product_qty
            })

        return {'value': result_dict}

