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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

# dummy call to workaround strptime bug (https://bugs.launchpad.net/openobject-server/+bug/947231/comments/8):
# datetime.datetime.strptime('2012-01-01 11:11:11', DEFAULT_SERVER_DATETIME_FORMAT)


class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    
    def _get_stock_picking_years(self, cr, uid, fields, context=None):
        result = []
        first_stock_picking_id = self.search(cr, uid, [('date', '!=', False)], order='date asc', limit=1, context=context)
        if first_stock_picking_id:
            first_stock_picking = self.browse(cr, uid, first_stock_picking_id[0], context)
            first_year = datetime.datetime.strptime(first_stock_picking.date, DEFAULT_SERVER_DATETIME_FORMAT).year
        else:
            first_year = datetime.date.today().year
        
        for year in range(int(first_year), int(datetime.date.today().year) + 1):
            result.append((str(year), str(year)))
        
        return result

    def _get_stock_picking_year(self, cr, uid, ids, field_name, arg, context):
        stock_pickings = self.browse(cr, uid, ids, context)

        result = {}

        for stock_picking in stock_pickings:
            if stock_picking.date:
                result[stock_picking.id] = datetime.datetime.strptime(stock_picking.date,
                                                                      DEFAULT_SERVER_DATETIME_FORMAT).year
            else:
                result[stock_picking.id] = False

        return result

    _columns = {
        'year': fields.function(_get_stock_picking_year, 'Year', type='selection', selection=_get_stock_picking_years,
                                method=True, help="Select year"),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'product_id': fields.related('move_lines', 'product_id', type='many2one', relation='product.product',
                                     string='Product'),
    }
    
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_args = []
        for arg in args:
            if arg[0] == 'year':
                new_args.append(('date', '>=', '{year}-01-01'.format(year=arg[2])))
                new_args.append(('date', '<=', '{year}-12-31'.format(year=arg[2])))
            else:
                new_args.append(arg)
                
        return super(stock_picking, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
