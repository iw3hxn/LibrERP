# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order'

    _columns = {
        # 'order_requirement_ids': fields.many2many('order.requirement', string='Order Requirements', readonly=True),
        # 'order_requirement_line_ids': fields.many2many('order.requirement.line', string='Order Requirement Lines', readonly=True),
        'sale_order_ids': fields.many2many('sale.order', string='Sale Orders', readonly=True),
    }

