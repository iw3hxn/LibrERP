# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import netsvc


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _action_check_goods_ready_hook(self, cr, uid, stock_move_ids, context):
        res = super(StockMove, self)._action_check_goods_ready_hook(cr, uid, stock_move_ids, context)

        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        mrp_production_obj = self.pool['mrp.production']
        mrp_product_produce_obj = self.pool['mrp.product.produce']

        wf_service = netsvc.LocalService("workflow")

        for stock_move in self.browse(cr, uid, stock_move_ids, context):
            sale_id = stock_move.sale_id.id
            temp_mrp_bom_ids = temp_mrp_bom_obj.search(cr, uid, [('sale_order_id', '=', sale_id),
                                                                 ('mrp_production_id', '!=', False)], context=context)
            for temp in temp_mrp_bom_obj.browse(cr, uid, temp_mrp_bom_ids, context):
                mrp_production = temp.mrp_production_id
                wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_confirm', cr)
                mrp_production_obj.force_production(cr, uid, [mrp_production.id])
                wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_produce', cr)

                # wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, '586', cr)
                # TODO: Manca mrp_product_produce.do_produce, ids ???
                # mrp_product_produce_obj.do_produce(cr, uid, ids, 'active_id': mrp_production.id

                # for production in prod_obj_pool.browse(cr, uid, [prod_obj.id], context= None):
                #     if production.move_lines or production.move_created_ids:
                #         prod_obj_pool.action_produce(cr,uid, production.id, production.product_qty, 'consume_produce', context = None)
                # wf_service.trg_validate(uid, 'mrp.production', oper_obj.production_id.id, 'button_produce_done', cr)

        return res
