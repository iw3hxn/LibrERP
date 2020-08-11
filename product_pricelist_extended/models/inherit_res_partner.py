# -*- coding: utf-8 -*-
# © 2020 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _


class SaleOrder(orm.Model):
    _inherit = 'res.partner'

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(SaleOrder, self).default_get(cr, uid, fields, context=context)
        if res.get('property_product_pricelist'):
            own_pricelist_id = self.pool['sale.order']._get_own_pricelist(cr, uid, context)
            if own_pricelist_id:
                res['property_product_pricelist'] = own_pricelist_id
        return res

