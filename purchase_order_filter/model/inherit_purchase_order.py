# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014-2016 Didotech srl (<http://www.didotech.com>).
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
from datetime import datetime


class purchase_order(orm.Model):

    _inherit = 'purchase.order'
    
    def _get_order_years(self, cr, uid, fields, context=None):
        result = []
        first_order_id = self.search(cr, uid, [('date_order', '!=', False)], order='date_order asc', limit=1, context=context)
        if first_order_id:
            first_order = self.browse(cr, uid, first_order_id[0], context)
            first_year = datetime.strptime(first_order.date_order, '%Y-%m-%d').year
        else:
            first_year = datetime.today().year
        
        for year in range(int(first_year), int(datetime.today().year) + 1):
            result.append((str(year), str(year)))
        
        return result
        
    def _get_order_year(self, cr, uid, ids, field_name, arg, context):
        orders = self.browse(cr, uid, ids, context)
        result = {}
        for order in orders:
            if order.date_order:
                result[order.id] = datetime.strptime(order.date_order, '%Y-%m-%d').year
            else:
                result[order.id] = False
                
        return result
    
    _columns = {
        'year': fields.function(_get_order_year, 'Year', type='selection', selection=_get_order_years, method=True, help="Select year"),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
    }

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_args = []

        for arg in args:
            if arg[0] == 'year':
                new_args.append(('date_order', '>=', '{year}-01-01'.format(year=arg[2])))
                new_args.append(('date_order', '<=', '{year}-12-31'.format(year=arg[2])))
            else:
                new_args.append(arg)
                
        return super(purchase_order, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
