# -*- coding: utf-8 -*-
# © 2019 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    # this is for not creating manufacture (create pickings but *NO* procurements)
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        res = super(SaleOrder, self)._create_pickings_and_procurements(cr, uid, order, order_lines, picking_id, context)

        order_requirement_obj = self.pool['order.requirement']
        order_requirement_line_obj = self.pool['order.requirement.line']
        sale_order_line_obj = self.pool['sale.order.line']

        if self.service_only(cr, uid, [order], context):
            order_req_id = self._create_order_requirement(cr, uid, order, context)
        else:
            order_req_id = order_requirement_obj.search(cr, uid, [('sale_order_id', '=', order.id)], context=context)[0]

        # For every sale.order.line => one order.requirement.line
        for line in order.order_line:
            # TODO: change it if you want to include services (maybe for creating routings)
            if line.product_id.type == 'service':
                ord_req_line_vals = {
                    'sale_order_line_id': line.id,
                    'product_id': line.product_id.id,
                    'qty': line.product_uom_qty,
                    'order_requirement_id': order_req_id,
                    'user_id': line.order_id.shop_id.project_manager_id and line.order_id.shop_id.project_manager_id.id or False,
                    'planned_hours': line.product_id and line.product_id.standard_service_time or 1,
                }
                ordreqline_id = order_requirement_line_obj.create(cr, uid, ord_req_line_vals, context)
                # sale_order_line_obj.write(cr, uid, line.id, {'order_requirement_line_id': ordreqline_id}, context)

        return res
