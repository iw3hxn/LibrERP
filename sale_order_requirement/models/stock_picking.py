# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)
# © 2018-2019 Andrei Levin - Didotech srl (www.didotech.com)

import logging

import netsvc
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _purchase_orders(self, cr, uid, ids, name, args, context=None):
        # Get the order state by order requirement line, from sale order id
        context = context or self.pool['res.users'].context_get(cr, uid)
        ordreqline_obj = self.pool['order.requirement.line']
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):

            done = 0
            tot = 0

            done_approved = 0
            tot_approved = 0

            state_str = ''
            purchase_orders_state = ''

            for line in picking.move_lines:

                try:
                    ordreqline_ids = ordreqline_obj.search(cr, uid, [('sale_order_line_id', '=', line.sale_line_id.id), ('new_product_id', '=', line.product_id.id)], context=context)

                    for ordreqline in ordreqline_obj.browse(cr, uid, ordreqline_ids, context):
                        d, t = ordreqline_obj.get_purchase_orders_state(ordreqline)
                        done += d
                        tot += t

                        d_approved, t_approved = ordreqline_obj.get_purchase_orders_approved(ordreqline)
                        done_approved += d_approved
                        tot_approved += t_approved

                except Exception as e:
                    _logger.error('_purchase_orders_state ' + e.message)
                    purchase_orders_state = ''
                    state_str = ''

            if tot > 0:
                purchase_orders_state = '{0}/{1}'.format(done, tot)

            if tot_approved > 0:
                state_str = '{0}/{1}'.format(done_approved, tot_approved)

            res[picking.id] = {
                'purchase_orders_approved': state_str,
                'purchase_orders_state': purchase_orders_state
            }

        return res

    _columns = {
        'sale_order_ids': fields.related(
            'move_lines', 'purchase_line_id', 'temp_mrp_bom_ids',
            'order_requirement_line_id', 'order_requirement_id', 'sale_order_id',
            string='Sale Orders', relation='sale.order', type='many2one'),
        'purchase_orders_approved': fields.function(_purchase_orders, method=True, type='char', size=128, multi="purchase_orders",
                                                    string='Purch. orders approved', readonly=True),
        'purchase_orders_state': fields.function(_purchase_orders, method=True, type='char', size=128,  multi="purchase_orders",
                                                 string='Incoming Deliveries', readonly=True),
    }

    def action_done(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")

        result = super(stock_picking, self).action_done(cr, uid, ids, context=context)

        for picking in self.browse(cr, uid, ids, context):
            if picking.sale_id and picking.sale_id.id and picking.type == 'out':
                if not self.search(cr, uid, [('sale_id', '=', picking.sale_id.id), ('type', '=', 'out'),
                                             ('state', '!=', 'done')], context=context):
                    wf_service.trg_validate(uid, 'sale.order', picking.sale_id.id, 'close_sale_order', cr)

        return result
