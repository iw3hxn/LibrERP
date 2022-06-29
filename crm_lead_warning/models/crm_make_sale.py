# -*- encoding: utf-8 -*-
from osv import osv


class CrmMakeSale(osv.osv_memory):
    _inherit = 'crm.make.sale'

    def onchange_partner(self, cr, uid, ids, part_id):
        res = self.pool['sale.order'].onchange_partner_id(cr, uid, [], part_id)
        return {
            'value': {},
            'warning': res.get('warning', {})
        }

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(CrmMakeSale, self).default_get(cr, uid, fields_list, context)
        if res.get('partner_id'):
            partner_id = res['partner_id']
            if isinstance(partner_id, tuple):
                partner_id = partner_id[0]
            self.pool['sale.order'].onchange_partner_id(cr, uid, [], partner_id)

        return res

    def makeOrder(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for make in self.browse(cr, uid, ids, context=context):
            self.pool['sale.order'].onchange_partner_id(cr, uid, [], make.partner_id.id)
        return super(CrmMakeSale, self).makeOrder(cr, uid, ids, context)
