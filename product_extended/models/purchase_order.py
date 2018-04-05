# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2012 Avanzosc <http://www.avanzosc.com>
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

import time
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID


class purchase_order(orm.Model):
    _inherit = "purchase.order"

    def wkf_approve_order(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).wkf_approve_order(cr, uid, ids, context)
        self.update_product(cr, uid, ids, context)
        return res

    def _get_product_unit_price(self, cr, uid, ids, to_currency, order_line, context):
        from_currency = order_line.order_id.pricelist_id.currency_id.id
        price_subtotal = self.pool['res.currency'].compute(
            cr, uid,
            from_currency_id=from_currency,
            to_currency_id=to_currency,
            from_amount=order_line.price_subtotal,
            context=context
        )
        return price_subtotal / order_line.product_qty

    def update_product(self, cr, uid, ids, context):
        supplierinfo_obj = self.pool['product.supplierinfo']
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        to_currency = user.company_id.currency_id.id
        for order in self.browse(cr, uid, ids, context):
            for line in order.order_line:
                if line.product_id:
                    vals = {
                        # 'last_purchase_date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'last_purchase_date': order.date_order or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'last_supplier_id': line.partner_id.id,
                        'last_purchase_order_id': order.id,
                    }

                    self.pool['product.product'].write(cr, SUPERUSER_ID, line.product_id.id, vals, context)
                    supplierinfo_ids = supplierinfo_obj.search(cr, uid, [('product_id', '=', line.product_id.id), ('name', '=', line.partner_id.id)], context=context)
                    if not supplierinfo_ids:
                        supplierinfo_ids = supplierinfo_obj.search(cr, uid, [('product_id', '=', line.product_id.id)], context=context)
                        sequence = 10
                        if supplierinfo_ids:
                            sequence = supplierinfo_obj.browse(cr, uid, supplierinfo_ids[-1], context).sequence + 10

                        price_unit = self._get_product_unit_price(cr, uid, ids, to_currency, line, context)

                        pricelist_vals = {
                            'min_quantity': 1,
                            'name': order.name,
                            'price': price_unit,
                        }

                        supplierinfo_obj.create(cr, uid, {
                            'name': line.partner_id.id,
                            'product_name': line.name,
                            'product_id': line.product_id.id,
                            'min_qty': 1,
                            'product_code': line.product_id.default_code,
                            'pricelist_ids': [(0, 0, pricelist_vals)],
                            'sequence': sequence
                        }, context)
        return True
