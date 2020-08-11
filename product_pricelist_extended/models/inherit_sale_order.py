# -*- coding: utf-8 -*-
# © 2020 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def _get_own_pricelist(self, cr, uid, context):
        users_obj = self.pool['res.users']
        if users_obj.has_group(cr, uid, 'product_pricelist_extended.group_only_my_pricelist'):
            pricelist_ids = self.pool['product.pricelist'].search(cr, uid, [('type', '=', 'sale'), ('member_ids', 'in', [uid])],
                                                                  context=context)
            if pricelist_ids:
                return pricelist_ids[0]
        return False

    def onchange_shop_id(self, cr, uid, ids, shop_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(SaleOrder, self).onchange_shop_id(cr, uid, ids, shop_id, context=context)
        if res.get('value') and shop_id:
            own_pricelist_id = self._get_own_pricelist(cr, uid, context)
            if own_pricelist_id:
                res['value']['pricelist_id'] = own_pricelist_id
        return res

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(SaleOrder, self).onchange_partner_id(cr, uid, ids, part)
        if res.get('value', False) and part:
            own_pricelist_id = self._get_own_pricelist(cr, uid, context)
            if own_pricelist_id:
                res['value']['pricelist_id'] = own_pricelist_id
        return res
