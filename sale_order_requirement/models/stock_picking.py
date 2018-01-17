# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import netsvc


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'sale_order_ids': fields.related(
            'move_lines', 'purchase_line_id', 'temp_mrp_bom_ids',
            'order_requirement_line_id', 'order_requirement_id', 'sale_order_id',
            string='Sale Orders', relation='sale.order', type='many2one'),
    }

    def action_done(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")

        result = super(stock_picking, self).action_done(cr, uid, ids, context=context)

        for picking in self.browse(cr, uid, ids, context):
            if picking.sale_id and picking.sale_id.id:
                wf_service.trg_validate(uid, 'sale.order', picking.sale_id.id, 'close_sale_order', cr)

        return result
