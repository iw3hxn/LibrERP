# -*- encoding: utf-8 -*-
from openerp.osv import orm, fields


class CrmLead(orm.Model):
    _inherit = 'crm.lead'

    def onchange_partner_id(self, cr, uid, ids, part, email=False, context=None):
        res = super(CrmLead, self).onchange_partner_id(cr, uid, ids, part, email, context)
        self.pool['sale.order'].onchange_partner_id(cr, uid, [], part)
        return res
