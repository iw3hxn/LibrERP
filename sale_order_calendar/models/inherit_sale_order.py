# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import orm, fields
from tools import ustr
from tools.translate import _


class sale_order(orm.Model):

    _inherit = "sale.order"

    _columns = {
        'date_action_next': fields.datetime('Date Next Action'),
        'next_activity_id': fields.many2one("crm.activity", string="Next Activity"),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        if not context.get('versioning', False):
            default.update({
                'date_action_next': False,
                'next_activity_id': False
            })
        return super(sale_order, self).copy(cr, uid, id, default, context)


