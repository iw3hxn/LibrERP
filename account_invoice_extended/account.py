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
from openerp import pooler

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'supplier_invoice_number': fields.char('Supplier invoice nr', size=16),
    }
    
    def copy(self, cr, uid, order_id, defaults, context=None):
        defaults['user_id'] = uid
        return super(account_invoice, self).copy(cr, uid, order_id, defaults, context)

    # override to group product_id too
    def inv_line_characteristic_hashcode(self, invoice, invoice_line):
        """Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""
        return "%s-%s-%s-%s"%(
            invoice_line['account_id'],
            invoice_line.get('tax_code_id', "False"),#invoice_line.get('product_id',"False"),
            invoice_line.get('analytic_account_id', "False"),
            invoice_line.get('date_maturity', "False"))

    #override to merge description (after will be trunked to x character everyway)
    def group_lines(self, cr, uid, iml, line, inv):
        """Merge account move lines (and hence analytic lines) if invoice line hashcodes are equals"""
        if inv.journal_id.group_invoice_lines:
            line2 = {}
            for x, y, l in line:
                tmp = self.inv_line_characteristic_hashcode(inv, l)

                if tmp in line2:
                    am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
                    line2[tmp]['debit'] = (am > 0) and am or 0.0
                    line2[tmp]['credit'] = (am < 0) and -am or 0.0
                    line2[tmp]['tax_amount'] += l['tax_amount']
                    line2[tmp]['analytic_lines'] += l['analytic_lines']
                    line2[tmp]['amount_currency'] += l['amount_currency']
                    line2[tmp]['quantity'] += l['quantity']
                    line2[tmp]['name'] += l['name']
                else:
                    line2[tmp] = l
            line = []
            for key, val in line2.items():
                line.append((0,0,val))
        return line


    def unlink(self, cr, uid, ids, context=None):
        #account_invoice_line_obj = self.pool['account.invoice.line']
        stock_picking_obj = self.pool['stock.picking']
        origins = {}
        for invoice in self.browse(cr, uid, ids, context):
            for line in invoice.invoice_line:
                line_origin = line.origin or False
                if line_origin not in origins:
                    origins[line_origin] = invoice.id

        # now on origins i have all the origin and invoice.id
        for origin in origins:
            if origin and len(origin.split(':')) == 2:
                # OUTxxx:SOyy
                pickings_name = origin.split(':')[0]
                picking_id = stock_picking_obj.search(cr, uid, [('name', '=', pickings_name)], context=context)
                if super(account_invoice, self).unlink(cr, uid, [origins[origin]], context=context):
                    if picking_id:
                        stock_picking_obj.write(cr, uid, [picking_id[0]], {'invoice_state': '2binvoiced'}, context=context)
                # now i need to eliminate other ids
                if origins[origin] in ids:
                    del ids[ids.index(origins[origin])]

        return super(account_invoice, self).unlink(cr, uid, ids, context=context)


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    def get_precision_tax():
        def change_digit_tax(cr):
            res = pooler.get_pool(cr.dbname).get('decimal.precision').precision_get(cr, 1, 'Account')
            return (17, res+3)
        return change_digit_tax

    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute=get_precision_tax()),
    }