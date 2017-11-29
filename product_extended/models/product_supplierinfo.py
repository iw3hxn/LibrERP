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
import time

import decimal_precision as dp
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class product_supplierinfo(orm.Model):
    _inherit = 'product.supplierinfo'

    def _get_cost_price(self, cr, uid, ids, field_name, arg, context):
        result = {}
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        ctx = {
            'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        }
        for supplier_cost in self.browse(cr, uid, ids, context):
            pricelist = supplier_cost.name.property_product_pricelist_purchase
            price = self.pool['product.pricelist'].price_get(cr, uid, [pricelist.id], supplier_cost.product_id.id, 1, supplier_cost.name.id, context=ctx)[pricelist.id] or 0
            if pricelist:
                from_currency = pricelist.currency_id.id
                to_currency = user.company_id.currency_id.id
                price_subtotal = self.pool['res.currency'].compute(
                    cr, uid,
                    from_currency_id=from_currency,
                    to_currency_id=to_currency,
                    from_amount=price,
                    context=context
                )
            result[supplier_cost.id] = price_subtotal or price or 0.0
        return result

    _columns = {
        'cost_price': fields.function(_get_cost_price, type='float', string="Cost Price", digits_compute=dp.get_precision('Purchase Price')),
        'list_price': fields.related('pricelist_ids', 'price', type='float', string="Price", digits_compute=dp.get_precision('Purchase Price'), ),
    }

