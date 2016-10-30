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
import decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class wizard_expense_line(orm.TransientModel):
    _name = 'wizard.expense.line'
    
    # Function is disabled, because values arrives not translated
    #def _get_payer(self, cr, uid, context=None):
        #return self.pool['hr.expense.line']._columns['payer'].selection
    
    #def _amount(self, cr, uid, ids, field_name, arg, context=None):
    #    if ids:
    #        result = {}
    #    else:
    #        return {}
    #
    #    wizards = self.browse(cr, uid, ids)
    #    for wizard in wizards:
    #        result['wizard.id'] = wizard.unit_amount * wizard.unit_quantity
    #   
    #    return result
    
    def _get_date_value(self, cr, uid, context):
        date_value = context.get('date_value', False)
        if date_value:
            date = datetime.strptime(date_value, DEFAULT_SERVER_DATETIME_FORMAT)
            date = date.date().strftime(DEFAULT_SERVER_DATE_FORMAT)
        else:
            date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)        

        return date
    
    _columns = {
        'name': fields.char('Expense Note', size=128, required=True),
        'date_value': fields.date('Date', required=True),
        #'total_amount': fields.function(_amount, string='Total', digits_compute=dp.get_precision('Account')),
        'unit_amount': fields.float('Unit Price', digits_compute=dp.get_precision('Account')),
        'unit_quantity': fields.float('Quantities'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('hr_expense_ok', '=', True)]),
        'ref': fields.char('Reference', size=32),
        # Function is disabled, because values arrives not translated
        #'payer': fields.selection(_get_payer, _('Payer'), translate=True, required=True),
        'payer': fields.selection((
            ('company', _('Company')),
            ('employee', _('Employee')),
            ('other', _('Other')),
        ), _('Payer'), required=True),
        
        'wizard_id': fields.many2one('task.time.control.confirm.wizard', 'Wizard')
    }
    
    _defaults = {
        'unit_quantity': 1,
        'date_value': _get_date_value,
    }
    
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        res = {}
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            res['name'] = product.name
            amount_unit = product.price_get('standard_price')[product.id]
            res['unit_amount'] = amount_unit
            
        return {'value': res}
    

class task_time_control_confirm_wizard(orm.TransientModel):
    _inherit = 'task.time.control.confirm.wizard'
    
    _columns = {
        'expense_line_ids': fields.one2many('wizard.expense.line', 'wizard_id', 'Expenses'),
        'user_id': fields.many2one("res.users", 'User')
    }
    
    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }

    def close_confirm(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        confirm_wizard = self.browse(cr, uid, ids[0], context)
        if self.pool['res.groups'].user_in_group(cr, uid, uid, 'base.group_user', context):
            employee = self.pool['hr.employee'].get_employee(cr, uid, uid)
            expense_values = {
                'employee_id': employee.id,
                'company_id': employee.user_id.company_id.id,
                'journal_id': False,
                'user_valid': False,
                'department_id': False
            }

            #if confirm_wizard.task_date:
            #    force_date = datetime.strptime(confirm_wizard.task_date, DEFAULT_SERVER_DATETIME_FORMAT)
            #    force_date = force_date.date().strftime(DEFAULT_SERVER_DATE_FORMAT)
            #else:
            #    force_date = False

            for expense_line in confirm_wizard.expense_line_ids:
                expense_values['date'] = expense_line.date_value
                hr_expense_id = self.pool['hr.expense.expense'].create(cr, uid, expense_values, context)

                values = {
                    'task_id': confirm_wizard.started_task.id,
                    'name': expense_line.name,
                    'date_value': expense_line.date_value,
                    'unit_amount': expense_line.unit_amount,
                    'unit_quantity': expense_line.unit_quantity,
                    'product_id': expense_line.product_id.id,
                    'ref': expense_line.ref,
                    'payer': expense_line.payer,
                    'expense_id': hr_expense_id
                }
                self.pool['hr.expense.line'].create(cr, uid, values, context)
        else:
            context['no_analytic_entry'] = True
        
        return super(task_time_control_confirm_wizard, self).close_confirm(cr, uid, ids, context)
