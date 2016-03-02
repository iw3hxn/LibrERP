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
import datetime


class account_invoice(orm.Model):
    _inherit = 'account.invoice'
    
    def _get_invoice_years(self, cr, uid, fields, context=None):
        result = []
        first_invoice_id = self.search(cr, uid, [('date_invoice', '!=', False)], order='date_invoice asc', limit=1)
        if first_invoice_id:
            first_invoice = self.browse(cr, uid, first_invoice_id[0])
            first_year = datetime.datetime.strptime(first_invoice.date_invoice, '%Y-%m-%d').year
        else:
            first_year = datetime.date.today().year
        
        for year in range(int(first_year), int(datetime.date.today().year) + 1):
            result.append((str(year), str(year)))
        
        return result
        
    def _get_invoice_year(self, cr, uid, ids, field_name, arg, context):
        invoices = self.browse(cr, uid, ids)
        
        result = {}
        
        for invoice in invoices:
            if invoice.date_invoice:
                result[invoice.id] = datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').year
            else:
                result[invoice.id] = False
                
        return result
    
    _columns = {
        'year': fields.function(_get_invoice_year, 'Year', type='selection', selection=_get_invoice_years, method=True, help="Select year"),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'product_id': fields.related('invoice_line', 'product_id', type='many2one', relation='product.product', string='Product'),
    }
    
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_args = []
        for arg in args:
            if arg[0] == 'year':
                new_args.append(('date_invoice', '>=', '{year}-01-01'.format(year=arg[2])))
                new_args.append(('date_invoice', '<=', '{year}-12-31'.format(year=arg[2])))
            else:
                new_args.append(arg)
                
        return super(account_invoice, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
