# -*- coding: utf-8 -*-

from osv import orm, fields


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    _columns = {
        'requested_date': fields.date(string="Requested Date", help="Date requested by the customer for the sale."),
    }
