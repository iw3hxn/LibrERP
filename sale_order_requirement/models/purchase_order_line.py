# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'order_requirement_line_ids': fields.one2many('temp.mrp.bom', 'purchase_order_line_id', 'Order Lines', readonly=True,
                                      states={'draft': [('readonly', False)]}),
    }

