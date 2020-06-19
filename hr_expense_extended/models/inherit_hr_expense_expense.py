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
from openerp.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class hr_expense_expense(orm.Model):
    _inherit = 'hr.expense.expense'
    
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        expenses = self.browse(cr, uid, ids, context)
        res = []
        for expense in expenses:
            month = datetime.strptime(expense.date, DEFAULT_SERVER_DATE_FORMAT).month
            name = u"{month:0>2d} - {name}".format(month=month, name=expense.employee_id.name)
            res.append((expense.id, name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)
    
    _columns = {
        'name': fields.char('Description', size=128, required=False),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
    }
    
    def get_hr_expense(self, cr, uid, employee_id, expense_date):
        first_day = datetime(year=expense_date.year, month=expense_date.month, day=1)
        last_day = first_day + relativedelta(months=1) - relativedelta(days=1)
        
        expense_ids = self.search(cr, uid, [
            ('employee_id', '=', employee_id),
            ('date', '>=', first_day.strftime(DEFAULT_SERVER_DATE_FORMAT)),
            ('date', '<=', last_day.strftime(DEFAULT_SERVER_DATE_FORMAT))
        ])
        
        if expense_ids:
            return expense_ids[0]
        else:
            return False
    
    def create(self, cr, uid, values, context=None):
        employee_obj = self.pool['hr.employee']
        expense_date = datetime.strptime(values.get('date', datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)), DEFAULT_SERVER_DATE_FORMAT)
        employee = employee_obj.get_employee(cr, uid, uid)
        employee_id = values.get('employee_id', employee.id)
        hr_expense_id = self.get_hr_expense(cr, uid, employee_id, expense_date)
        real_employee = employee_obj.browse(cr, uid, employee_id, context)
        if not hr_expense_id:
            values['name'] = u"{month:0>2d} - {name}".format(month=expense_date.month, name=real_employee.name)
            if not values.get('currency_id', False):
                user = self.pool['res.users'].browse(cr, uid, uid)
                values['currency_id'] = user.company_id.currency_id.id
            
            hr_expense_id = super(hr_expense_expense, self).create(cr, uid, values, context)
        #
        # if values.get('line_ids', False):
        #     for expense_line in values['line_ids']:
        #         line_values = expense_line[2]
        #         line_values['expense_id'] = hr_expense_id
        #         self.pool['hr.expense.line'].create(cr, uid, line_values)

        hr_expense = self.browse(cr, uid, hr_expense_id, context)
        
        for expense_line in hr_expense.line_ids:
            if expense_line.task_id:
                analytic_values = {
                    'name': expense_line.name,
                    'product': expense_line.product_id,
                    'product_qty': expense_line.unit_quantity,
                    'account_id': expense_line.analytic_account.id,
                    'unit_amount': expense_line.unit_amount,
                    'date': expense_line.date_value + ' 00:00:00',
                    'ref': hr_expense.name,
                    'origin_document': expense_line
                }
                self.pool['account.analytic.line'].update_or_create_line(cr, uid, move=False, values=analytic_values, context=context)
        return hr_expense_id

    def write(self, cr, uid, ids, values, context=None):
        result = super(hr_expense_expense, self).write(cr, uid, ids, values, context)
        
        for hr_expense in self.browse(cr, uid, ids, context):
            for expense_line in hr_expense.line_ids:
                if expense_line.task_id:
                    analytic_values = {
                        'name': expense_line.name,
                        'product': expense_line.product_id,
                        'product_qty': expense_line.unit_quantity,
                        'account_id': expense_line.analytic_account.id,
                        'unit_amount': expense_line.unit_amount,
                        'date': expense_line.date_value + ' 00:00:00',
                        'ref': hr_expense.name,
                        'origin_document': expense_line
                    }
                    self.pool['account.analytic.line'].update_or_create_line(cr, uid, move=False, values=analytic_values, context=context)
        return result


class hr_expense_line(orm.Model):
    _inherit = 'hr.expense.line'

    _order = "date_value asc"
         
    _columns = {
        'task_id': fields.many2one('project.task', string='Project Task', domain="[('state', 'not in', ('draft',))]"),
        'payer': fields.selection((
            ('company', _('Company')),
            ('employee', _('Employee')),
            ('other', _('Other')),
        ), _('Payer'), required=True),
        # 'user_id': fields.related('expense_id', 'user_id', type='many2one', relation='res.user', string='User'),
    }

    _defaults = {
        'payer': 'employee',
    }
    
    def write(self, cr, uid, ids, values, context=None):
        if values.get('task_id', False):
            task = self.pool['project.task'].browse(cr, uid, values['task_id'], context)
            if task.project_id:
                values['analytic_account'] = task.project_id.analytic_account_id.id
        
        if values.get('product_id', False) and not values.get('uom_id', False):
            product = self.pool['product.product'].browse(cr, uid, values['product_id'])
            values['uom_id'] = product.uom_id.id
        return super(hr_expense_line, self).write(cr, uid, ids, values, context)

    def create(self, cr, uid, values, context=None):
        if values.get('task_id', False):
            task = self.pool['project.task'].browse(cr, uid, values['task_id'], context)
            if task.project_id:
                values['analytic_account'] = task.project_id.analytic_account_id.id

        if values.get('product_id', False) and not values.get('uom_id', False):
            product = self.pool['product.product'].browse(cr, uid, values['product_id'], context)
            values['uom_id'] = product.uom_id and product.uom_id.id or 1
        
        return super(hr_expense_line, self).create(cr, uid, values, context)
    
    def unlink(self, cr, uid, ids, context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        for line in self.browse(cr, uid, ids, context):
            analytic_line_ids = analytic_line_obj.search(cr, uid, [('origin_document', '=', '{model}, {document_id}'.format(model=line._name, document_id=line.id))])
            if analytic_line_ids:
               analytic_line_obj.unlink(cr, uid, analytic_line_ids, context)
        return super(hr_expense_line, self).unlink(cr, uid, ids, context)
