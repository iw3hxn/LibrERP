# -*- encoding: utf-8 -*-
##############################################################################
#


from openerp.osv import orm, fields


class sale_order_confirm_line(orm.TransientModel):
    _inherit = "sale.order.confirm.line"

    _columns = {
        'requested_date': fields.date(string="Requested Date", help="Date requested by the customer for the sale."),
    }

    def onchange_requested_date(self, cr, uid, ids, requested_date, sale_line_id, context=None):
        if requested_date:
            self.pool['sale.order.line'].write(cr, uid, sale_line_id, {'requested_date': requested_date}, context)
        result = {}
        return {'value': result}
