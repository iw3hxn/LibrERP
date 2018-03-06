# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _


class sale_order(orm.Model):
    _inherit = 'sale.order'

    # this is for not creating manufacture (create pickings but *NO* procurements)
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context['stop_procurement'] = True
        res = super(sale_order, self)._create_pickings_and_procurements(
            cr, uid, order, order_lines, picking_id, context)

        order_requirement_obj = self.pool['order.requirement']
        order_requirement_line_obj = self.pool['order.requirement.line']
        sale_order_line_obj = self.pool['sale.order.line']

        # ONE sale.order => ONE order.requirement
        order_requirement_vals = {
            'sale_order_id': order.id,
            'note': order.note
        }
        order_req_id = order_requirement_obj.create(cr, uid, order_requirement_vals, context)

        # For every sale.order.line => one order.requirement.line
        for line in order.order_line:
            # TODO: change it if you want to include services (maybe for creating routings)
            if line.product_id.type != 'service':
                ord_req_line_vals = {
                    'sale_order_line_id': line.id,
                    'product_id': line.product_id.id,
                    'qty': line.product_uom_qty,
                    'order_requirement_id': order_req_id,
                }
                ordreqline_id = order_requirement_line_obj.create(cr, uid, ord_req_line_vals, context)
                sale_order_line_obj.write(cr, uid, line.id, {'order_requirement_line_id': ordreqline_id}, context)

        return res

    def action_reopen(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            for line in order.order_line:
                if line.order_requirement_line_id:
                    raise orm.except_orm(
                        _('Error'),
                        _("You can't reopen Sale Order that already generated Requirement Order")
                    )

        return super(sale_order, self).action_reopen(cr, uid, ids, context=context)

    def _get_production_order(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        mrp_production_obj = self.pool['mrp.production']
        for order in self.browse(cr, uid, ids, context):
            mrp_production_ids = mrp_production_obj.search(cr, uid, [('sale_id', '=', order.id)], context=context)
            result[order.id] = mrp_production_ids
        return result

    _columns = {
        'internal_note': fields.text('Internal Note'),
        'mrp_production_ids': fields.function(_get_production_order, string="Production Order", type='one2many',
                                              method=True, relation='mrp.production'),
        'purchase_order_ids': fields.many2many('purchase.order', string='Purchase Orders', readonly=True)
    }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(sale_order, self)._prepare_order_picking(cr, uid, order, context)
        if order.internal_note:
            res['internal_note'] = order.internal_note
        return res
