# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import orm, fields
from tools import ustr
from tools.translate import _


class sale_order(orm.Model):

    _inherit = "sale.order"

    _columns = {
        'date_action_next': fields.datetime('Date Next Action'),
        'next_activity_id': fields.many2one("crm.activity", string="Next Activity")
    }




