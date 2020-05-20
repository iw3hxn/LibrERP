import datetime

import netsvc
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
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
        context = context or self.pool['res.users'].context_get(cr, uid)
        sale_order_line_obj = self.pool['sale.order.line']

        sale_order_line_ids = []
        if context.get('order_id'):
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
                order_requirement_line = self.pool['order.requirement.line'].browse(cr, uid, line_ids[0], context)
                order_requirement_line.write({'sale_order_line_id': line_id})

                order_requirement = self.pool['order.requirement'].browse(cr, uid, context['order_id'], context)

                # create picking
                pick_type = 'internal'
                ir_sequence_obj = self.pool['ir.sequence']
                stock_picking_obj = self.pool['stock.picking']

                pick_name = ir_sequence_obj.get(cr, uid, 'stock.picking.' + pick_type)
                order = order_requirement.sale_order_id
                date_planned = datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)

                picking_vals = {
                    'name': pick_name,
                    'origin': _('Order Requirement') + ' ' + order.name,
                    'date': date_planned,
                    'type': pick_type,
                    'state': 'auto',
                    'move_type': 'one',
                    'sale_id': order.id,
                    'address_id': order.partner_shipping_id.id,
                    'note': order.note,
                    'invoice_state': 'none',
                    'company_id': order.company_id.id,
                    'auto_picking': True,
                }
                if order.project_project:
                    project = order.project_project
                    picking_vals.update({
                        'project_id': project.id,
                        'account_id': project.analytic_account_id.id,
                        'sale_project': project.id
                    })

                picking_id = stock_picking_obj.create(cr, uid, picking_vals, context)

                location_id = order.shop_id.warehouse_id.lot_stock_id.id
                output_id = order.shop_id.warehouse_id.lot_output_id.id
                price_unit = 0.0

                if order_requirement_line.qty != 0.0:
                    price_unit = order_requirement_line.product_id.cost_price

                move_vals = {
                    'name': order_requirement_line.product_id.name[:250],
                    'picking_id': picking_id,
                    'product_id': order_requirement_line.product_id.id,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'product_qty': order_requirement_line.qty,
                    'product_uom': order_requirement_line.product_id.uom_id.id,
                    # 'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
                    # 'product_uos': (line.product_uos and line.product_uos.id) \
                    #                or line.product_uom.id,
                    # 'product_packaging': line.product_packaging.id,
                    # 'address_id': order.partner_shipping_id.id,
                    'location_id': location_id,
                    'location_dest_id': output_id,
                    'sale_line_id': line_id,
                    'tracking_id': False,
                    'state': 'draft',
                    # 'state': 'waiting',
                    'company_id': order.company_id.id,
                    'price_unit': price_unit
                }

                move_id = self.pool['stock.move'].create(cr, uid, move_vals, context)
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
                stock_picking_obj.force_assign(cr, uid, [picking_id], context)
                ctx = context.copy()
                ctx['force_commit'] = True
                stock_picking_obj._commit_cost(cr, uid, [picking_id], ctx)

        return True
