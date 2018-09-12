# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.


from openerp.osv import orm, fields


class sale_order_confirm(orm.TransientModel):
    _inherit = "sale.order.confirm"

    _columns = {
        'requested_date': fields.date(string="Requested Date", help="Date requested by the customer for the sale."),
    }

    def get_sale_order_confirm_line_vals(self, cr, uid, sale_order_line, context=None):
        res = super(sale_order_confirm, self).get_sale_order_confirm_line_vals(cr, uid, sale_order_line, context)
        if sale_order_line.requested_date:
            res.update({'requested_date': sale_order_line.requested_date})
        elif sale_order_line.order_id.requested_date:
            res.update({
                'requested_date': sale_order_line.order_id.requested_date,
            })
            sale_order_line.write({'requested_date': sale_order_line.order_id.requested_date,})
        return res

    def get_sale_order_line_vals(self, cr, uid, order_id, sale_order_line_data, context):
        res = super(sale_order_confirm, self).get_sale_order_line_vals(cr, uid, order_id, sale_order_line_data, context)
        return res

