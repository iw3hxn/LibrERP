# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2012 Avanzosc <http://www.avanzosc.com>
#    © 2014 - 2020 Didotech srl (www.didotech.com)
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

from openerp.osv import orm, fields
from openerp import SUPERUSER_ID


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def action_date_assign(self, cr, uid, ids, *args):
        res = super(account_invoice, self).action_date_assign(cr, uid, ids, *args)
        context = self.pool['res.users'].context_get(cr, uid)
        self.update_product(cr, uid, ids, context)
        return res

    def update_product(self, cr, uid, ids, context):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        to_currency = user.company_id.currency_id.id
        for invoice in self.browse(cr, uid, ids, context):
            from_currency = invoice.currency_id.id
            for line in invoice.invoice_line:
                if line.product_id and line.quantity != 0.0 and line.price_unit != 0.0:
                    if invoice.type == 'out_invoice':
                        price_subtotal = self.pool['res.currency'].compute(
                            cr, uid,
                            from_currency_id=from_currency,
                            to_currency_id=to_currency,
                            from_amount=line.price_subtotal,
                            context=context
                        )
                        vals = {
                            'last_sale_price': price_subtotal / line.quantity,
                            'last_customer_invoice_id': invoice.id
                        }
                        self.pool['product.product'].write(cr, SUPERUSER_ID, line.product_id.id, vals, context)
                    elif invoice.type == 'in_invoice':
                        price_subtotal = self.pool['res.currency'].compute(
                            cr, uid,
                            from_currency_id=from_currency,
                            to_currency_id=to_currency,
                            from_amount=line.price_subtotal,
                            context=context
                        )

                        # divide by quantity multiplied by UoM factor
                        factor_inv = line.product_id.uom_po_id and line.product_id.uom_po_id.factor_inv or 1
                        unit_purchase_price = price_subtotal / (line.quantity * factor_inv)

                        vals = {
                            'last_purchase_price': unit_purchase_price,
                            'last_supplier_invoice_id': invoice.id
                        }
                        if line.product_id.cost_method == 'lpp':
                            vals.update({
                                'standard_price': unit_purchase_price
                            })

                        self.pool['product.product'].write(cr, SUPERUSER_ID, line.product_id.id, vals, context)
        return True
