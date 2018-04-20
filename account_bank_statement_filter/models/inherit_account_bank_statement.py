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


class account_bank_statement(orm.Model):
    _inherit = 'account.bank.statement'
    
    def _get_statement_years(self, cr, uid, fields, context=None):
        result = []
        first_statement_id = self.search(cr, uid, [('date', '!=', False)], order='date asc', limit=1, context=context)
        if first_statement_id:
            first_statement = self.browse(cr, uid, first_statement_id[0], context)
            first_year = datetime.datetime.strptime(first_statement.date, '%Y-%m-%d').year
        else:
            first_year = datetime.date.today().year
        
        for year in range(int(first_year), int(datetime.date.today().year) + 1):
            result.append((str(year), str(year)))
        
        return result
        
    def _get_statement_year(self, cr, uid, ids, field_name, arg, context):
        
        result = {}
        for statement in self.browse(cr, uid, ids, context):
            if statement.date:
                result[statement.id] = datetime.datetime.strptime(statement.date, '%Y-%m-%d').year
            else:
                result[statement.id] = False
                
        return result
    
    _columns = {
        'year': fields.function(_get_statement_year, 'Year', type='selection', selection=_get_statement_years, method=True, help="Select year"),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'partner_id': fields.related('line_ids', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
    }
    
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_args = []
        for arg in args:
            if arg[0] == 'year':
                new_args.append(('date', '>=', '{year}-01-01'.format(year=arg[2])))
                new_args.append(('date', '<=', '{year}-12-31'.format(year=arg[2])))
            else:
                new_args.append(arg)
                
        return super(account_bank_statement, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
