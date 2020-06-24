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
from product._common import rounding
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class project_task(orm.Model):
    _inherit = 'project.task'
    
    _columns = {
        'expense_line_ids': fields.one2many('hr.expense.line', 'task_id', 'Expenses'),
    }
    
    def create(self, cr, uid, values, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        task_id = super(project_task, self).create(cr, uid, values, context)
        task = self.browse(cr, uid, task_id, context)
        
        if task.expense_line_ids:
            # add hr_expense_expense
            employee = self.pool['hr.employee'].get_employee(cr, uid, uid, context)
            if employee:
                expense_values = {
                    # 'note': False,
                    'employee_id': employee.id,
                    # 'invoice_id': False,
                    'company_id': values.get('company_id', 1),
                    'journal_id': False,
                    # 'currency_id': 1,
                    'user_valid': False,
                    'date': values.get('date', datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)),
                    # 'ref': False,
                    'department_id': False
                }

                hr_expense_id = self.pool['hr.expense.expense'].create(cr, uid, expense_values, context)
                line_ids = [expense_line.id for expense_line in task.expense_line_ids]
                self.pool['hr.expense.line'].write(cr, uid, line_ids, {'expense_id': hr_expense_id}, context)
        return task_id

    def write(self, cr, uid, ids, values, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        
        result = super(project_task, self).write(cr, uid, ids, values, context)
        
        for task in self.browse(cr, uid, ids, context):
            if values.get('expense_line_ids', False):
                # add hr_expense_expense
                employee = self.pool['hr.employee'].get_employee(cr, uid, uid, context)
                if employee:
                    expense_values = {
                        # 'note': False,
                        'employee_id': employee.id,
                        # 'invoice_id': False,
                        'company_id': task.company_id.id,
                        'journal_id': False,
                        # 'currency_id': 1,
                        'user_valid': False,
                        'date': values.get('date', datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)),
                        # 'ref': False,
                        'department_id': False
                    }

                    hr_expense_id = self.pool['hr.expense.expense'].create(cr, uid, expense_values, context)
                    line_ids = [expense_line.id for expense_line in task.expense_line_ids]
                    self.pool['hr.expense.line'].write(cr, uid, line_ids, {'expense_id': hr_expense_id}, context)
            
            for expense_line in task.expense_line_ids:
                if values.get('project_id', False):
                    self.pool['hr.expense.line'].write(cr, uid, [expense_line.id], {'analytic_account': task.project_id.analytic_account_id.id}, context)
                
                if expense_line.task_id and task.project_id:
                    analytic_values = {
                        'name': expense_line.name,
                        'product': expense_line.product_id,
                        'product_qty': expense_line.unit_quantity,
                        'account_id': task.project_id.analytic_account_id.id,
                        'unit_amount': expense_line.unit_amount,
                        'date': expense_line.date_value + ' 00:00:00',
                        'ref': task.name,
                        'origin_document': expense_line
                    }
                    self.pool['account.analytic.line'].update_or_create_line(cr, uid, move=False, values=analytic_values, context=context)
        return result
    #
    # def unlink(self, cr, uid, ids, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     for task in self.browse(cr, uid, ids, context):
    #         if task.expense_line_ids:
    #
    #     return super(project_task, self).unlink(cr, uid, ids, context)
