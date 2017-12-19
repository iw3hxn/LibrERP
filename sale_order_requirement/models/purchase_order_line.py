# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'order_requirement_ids': fields.many2many('order.requirement', string='Order Requirements', readonly=True),
        'order_requirement_line_ids': fields.many2many('order.requirement.line', string='Order Requirement Lines', readonly=True),
        'sale_order_ids': fields.many2many('sale.order', string='Sale Orders', readonly=True),
        # NOT possible to have related many2many => unsupported in OpenERP 6.1
        # 'sale_order_ids': fields.related('order_requirement_ids', 'sale_order_id', string='Sale Orders',
        #                                  relation='sale.order', type='many2many', readonly=True, store=False)
    }
