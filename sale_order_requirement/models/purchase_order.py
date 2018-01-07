# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    _columns = {
        'sale_order_ids': fields.many2many('sale.order', string='Sale Orders', readonly=True),
    }


class procurement_order(orm.Model):
    _inherit = 'procurement.order'

    def action_po_assign(self, cr, uid, ids, context=None):
        """ This is action which call from workflow to assign purchase order to procurements
        @return: True
        """
        return 0

