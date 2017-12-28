# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import netsvc


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _action_check_goods_ready_hook(self, cr, uid, stock_move_ids, context):
        stock_move_obj = self.pool['stock.move']
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        mrp_production_obj = self.pool['mrp.production']
        mrp_product_produce_obj = self.pool['mrp.product.produce']

        wf_service = netsvc.LocalService("workflow")

        for stock_move in stock_move_obj.browse(cr, uid, stock_move_ids, context):
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