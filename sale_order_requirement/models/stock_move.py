# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import netsvc


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _action_check_goods_ready_hook(self, cr, uid, stock_move_ids, context):
        res = super(StockMove, self)._action_check_goods_ready_hook(cr, uid, stock_move_ids, context)

        user = self.pool['res.users'].browse(cr, uid, uid, context)

        if not user.company_id.auto_production:
            return res

        mrp_production_obj = self.pool['mrp.production']
        order_requirement_line_obj = self.pool['order.requirement.line']
        wf_service = netsvc.LocalService("workflow")

        for stock_move in self.browse(cr, uid, stock_move_ids, context):
            sale_id = stock_move.sale_id and stock_move.sale_id.id or False
            sale_order_line_id = stock_move.sale_line_id and stock_move.sale_line_id.id or False
            if sale_id and sale_order_line_id:
                order_requirement_line_ids = order_requirement_line_obj.search(cr, uid, [('sale_order_line_id', '=', sale_order_line_id)], context=context)
                for order_requirement_line in order_requirement_line_obj.browse(cr, uid, order_requirement_line_ids, context):
                    for temp in order_requirement_line.temp_mrp_bom_ids:
                        mrp_production = temp.mrp_production_id or False
                        if mrp_production and mrp_production.state != 'done':
                            wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_confirm', cr)
                            wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'force_production', cr)
                            wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_produce', cr)
                            mrp_production_obj.action_produce(cr, uid, mrp_production.id, mrp_production.product_qty, 'consume_produce', context=context)

        return res
