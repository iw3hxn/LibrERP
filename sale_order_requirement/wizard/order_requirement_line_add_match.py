import datetime

import netsvc
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from tools.translate import _


class OrderRequirementLineAddMatch(orm.TransientModel):
    _name = "order.requirement.line.add.match"
    _description = "Add sale Order to line"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(OrderRequirementLineAddMatch, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            line = self.pool['order.requirement.line'].browse(cr, uid, context['active_id'], context=context)
            # if 'order_id' in fields:
            #     order_id = line.order_requirement_id.sale_order_id
            #     res.update(order_id=order_id.id)
        #     if 'product_id' in fields:
        #         res.update({'product_id': move.product_id.id})
        #     if 'product_uom' in fields:
        #         res.update({'product_uom': move.product_uom.id})
        #     if 'qty' in fields:
        #         res.update({'qty': move.product_qty})
        #     if 'use_exist' in fields:
        #         res.update({'use_exist': (move.picking_id and move.picking_id.type=='out' and True) or False})
        #     if 'location_id' in fields:
        #         res.update({'location_id': move.location_id.id})
        return res
    #

    def _get_order_id(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        purchase_order_obj = self.pool['purchase.order']
        purchase_order_ids = []
        if context.get('order_id'):
            order_domain = [('state', '=', 'draft')]
            if False:
                line = self.pool['order.requirement'].browse(cr, uid, context['order_id'], context=context)
                order_id = line.sale_order_id.id
                order_domain.append(('sale_order_ids', 'in', order_id))
            purchase_order_ids = purchase_order_obj.search(cr, uid, order_domain, context=context)
        res = purchase_order_obj.name_get(cr, uid, purchase_order_ids, context=context)

        return res

    _columns = {
        'order_id': fields.selection(_get_order_id, 'Purchase Order', required=True),
    }

    def link(self, cr, uid, ids, context=None):
        # context = context or self.pool['res.users'].context_get(cr, uid)
        # res = self._link(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}

    def _link(self, cr, uid, ids, line_ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        return True
