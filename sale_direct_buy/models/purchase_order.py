# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def print_purchase(self, cr, uid, ids, context):
        return self.pool['account.invoice'].print_report(cr, uid, ids, 'purchase.report_purchase_order', context)

    def _get_sale_order(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        sale_order_obj = self.pool['sale.order']
        purchase_requisition_obj = self.pool['purchase.requisition']
        for order in self.browse(cr, uid, ids, context):
            tender_sale_order_ids = []
            name = order.origin
            direct_sale_order_ids = sale_order_obj.search(cr, uid, [('name', 'ilike', name)], context=context)
            tender_ids = purchase_requisition_obj.search(cr, uid, [('name', 'ilike', name)], context=context)
            if tender_ids:
                for tender in purchase_requisition_obj.browse(cr, uid, tender_ids, context):
                    tender_sale_order_ids += sale_order_obj.search(cr, uid, [('name', 'ilike', tender.origin)], context=context)
            result[order.id] = direct_sale_order_ids + tender_sale_order_ids
        return result

    _columns = {
        'sale_order_ids': fields.function(_get_sale_order, string=_("Sale Order"), type='one2many', method=True, relation='sale.order')
    }


