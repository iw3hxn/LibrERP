# -*- encoding: utf-8 -*-


from openerp.osv import orm, fields


class StockMove(orm.Model):
    _inherit = 'stock.move'

    _columns = {
        'purchase_order_line_name': fields.related('purchase_line_id', 'name', type="char", string="Purchase description")
    }
