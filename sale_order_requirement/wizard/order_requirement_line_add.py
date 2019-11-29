import decimal_precision as dp
from openerp.osv import orm, fields
from tools.translate import _


class OrderRequirementLineAdd(orm.TransientModel):
    _name = "order.requirement.line.add"
    _description = "Split in Production lots"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(OrderRequirementLineAdd, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            line = self.pool['order.requirement.line'].browse(cr, uid, context['active_id'], context=context)
            if 'order_id' in fields:
                order_id = line.order_requirement_id.sale_order_id
                res.update(order_id=order_id.id)
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

    def _get_order_line(self, cr, uid, context=None):
        sale_order_line_obj = self.pool['sale.order.line']

        line = self.pool['order.requirement'].browse(cr, uid, context['order_id'], context=context)
        order_id = line.sale_order_id.id

        sale_order_line_ids = sale_order_line_obj.search(cr, uid, [('order_id', '=', order_id)], context=context)
        res = sale_order_line_obj.name_get(cr, uid, sale_order_line_ids, context=context)

        return res

    _columns = {
        'order_id': fields.many2one('sale.order', 'Order', required=True, select=True),
        'order_line': fields.selection(_get_order_line, 'Order Line', required=False),
        # 'order_line_id': fields.many2one('sale.order.line', 'Production Lots'),
        # 'order_line_ids': fields.one2many('stock.move.split.lines', 'wizard_id', 'Production Lots'),
    }

    def link(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = self._link(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}

    def _link(self, cr, uid, ids, line_ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for wizard in self.browse(cr, uid, ids, context):
            if wizard.order_line:
                line_id = int(wizard.order_line)
                self.pool['order.requirement.line'].write(cr, uid, line_ids, {'sale_order_line_id': line_id}, context=context)
        return True
