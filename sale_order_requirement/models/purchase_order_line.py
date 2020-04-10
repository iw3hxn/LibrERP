# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'order_requirement_ids': fields.many2many('order.requirement', string='Order Requirements', readonly=True),
        'order_requirement_line_ids': fields.many2many('order.requirement.line', string='Order Requirement Lines', readonly=True),
        'temp_mrp_bom_ids': fields.many2many('temp.mrp.bom', string='Sale Orders', readonly=True),
        # NOT possible to have related many2many => unsupported in OpenERP 6.1
        # 'sale_order_ids': fields.related('order_requirement_ids', 'sale_order_id', string='Sale Orders',
        #                                  relation='sale.order', type='many2many', readonly=True, store=False)
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        default.update({
            'order_requirement_ids': [],
            'order_requirement_line_ids': [],
            'temp_mrp_bom_ids': []
        })
        return super(PurchaseOrderLine, self).copy(cr, uid, ids, default, context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'order_requirement_ids': [],
            'order_requirement_line_ids': [],
            'temp_mrp_bom_ids': []
        })
        return super(PurchaseOrderLine, self).copy_data(cr, uid, id, default, context=context)
