# -*- coding: utf-8 -*-

from openerp.osv import orm


class PurchaseOrder(orm.Model):
    
    _inherit = "purchase.order"

    def copy(self, cr, uid, id, default=None, context=None):
        partner_id = self.read(cr, uid, id, ['partner_id'], context, load='_obj')['partner_id']
        res = self.pool['purchase.order'].onchange_partner_id(cr, uid, [], partner_id)
        return super(PurchaseOrder, self).copy(cr, uid, id, default, context)
