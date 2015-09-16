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

from openerp.osv import orm, fields


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def action_date_assign(self, cr, uid, ids, *args):
        res = super(account_invoice, self).action_date_assign(cr, uid, ids, *args)
        context = self.pool['res.users'].context_get(cr, uid)
        for invoice in self.browse(cr, uid, ids, context):
            for line in invoice.invoice_line:
                if line.product_id:
                    if invoice.type == 'out_invoice' and line.price_unit != 0.0:
                        line.product_id.write({'last_sale_price': line.price_unit})
                        # self.pool['product.product'].write(cr, uid, [line.product_id.id], ())
                    elif invoice.type == 'in_invoice' and line.price_unit != 0.0:
                        line.product_id.write({'last_purchase_price': line.price_unit})
                        # self.pool['product.product'].write(cr, uid, [line.product_id.id], ())
        return res
