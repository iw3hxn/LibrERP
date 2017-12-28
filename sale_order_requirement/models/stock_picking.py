# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import netsvc


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'sale_order_ids': fields.related('move_lines', 'purchase_line_id', 'temp_mrp_bom_ids', 'order_requirement_line_id', 'order_requirement_id', 'sale_order_id',
                                        string='Sale Orders', relation='sale.order', type='many2one'),
    }