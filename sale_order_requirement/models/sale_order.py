# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class sale_order(orm.Model):
    _inherit = 'sale.order'

    # this is for not creating manufacture (create pickings but *NO* procurements)
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context['stop_procurement'] = True
        res = super(sale_order, self)._create_pickings_and_procurements(cr, uid, order, order_lines, picking_id, context)

        order_requirement_obj = self.pool['order.requirement']
        order_req_id = order_requirement_obj.create(cr, uid, {'sale_order_id': order.id}, context)

        for line in order.order_line:
            if line.product_id.type != 'service':
                ord_req_line_vals = {
                    'product_id': line.product_id.id,
                    'qty': line.product_uom_qty
                }
                order_requirement_obj.write(cr, uid, order_req_id,
                                            {'order_requirement_line_ids': [(0, False, ord_req_line_vals)]}, context)

        return res

