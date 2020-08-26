# -*- coding: utf-8 -*-
from openerp.osv import orm


class ProcurementOrder(orm.Model):
    _inherit = 'procurement.order'

    def action_po_assign(self, cr, uid, ids, context=None):
        """ This is action which call from workflow to assign purchase order to procurements
        @return: True
        """
        return 0

