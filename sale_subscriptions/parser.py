# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2015 Didotech s.r.l. (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import netsvc

LOGGER = netsvc.Logger()

from report import report_sxw


class Parser(report_sxw.rml_parse):
    durations = {
        730: 24,
        365: 12,
        180: 6,
        90: 3,
        60: 2,
        30: 1,
    }
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'adjustPrice': self._adjust_price,
        })

    def _adjust_price(self, sale_order_line, price_unit):
        if (not sale_order_line.order_id.have_subscription) or (not sale_order_line.product_id.subscription):
            return price_unit
        
        duration = self.durations[sale_order_line.order_id.order_duration]
        invoice_duration = self.durations[sale_order_line.order_id.order_invoice_duration]
        if invoice_duration < duration:
            payments_quantity = duration / invoice_duration
        else:
            payments_quantity = 1   
         
        # Il price is for annual usage of a product
        return round(price_unit / 12 * duration / payments_quantity, 2)
