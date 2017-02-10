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


class res_company(orm.Model):
    _inherit = 'res.company'

    def _getWorkHourUoM(self, cr, uid, context=None):
        md = self.pool['ir.model.data']
        try:
            dummy, res_id = md.get_object_reference(cr, uid, 'product', 'uom_hour')
            check_right = self.pool['product.uom'].search(cr, uid, [('id', '=', res_id)], context=context)
            if check_right:
                return res_id
        except ValueError:
            pass
        return False
    
    _columns = {
        'delivery_note_journal_id': fields.many2one('account.analytic.journal', 'Delivery Note Journal'),
        'expense_journal_id': fields.many2one('account.analytic.journal', 'Expense Journal'),
        'work_order_default_task_ids': fields.one2many('template.task', 'company_id', string='Default Work Order Tasks'),
        'sale_task_matix_ids': fields.one2many('sale.order.task.matrix', 'company_id', string='Matrix Sale Order Line to Task'),
        'hour': fields.many2one('product.uom', 'Hour UoM', required=True),
        'create_task': fields.boolean('Create Task from Sale Order?'),
        'task_no_user': fields.boolean('Task without default user', help='If set the task will not have a user, so will be visible to all')
    }
    
    _defaults = {
        'create_task': True,
        'task_no_user': True,
        'hour': _getWorkHourUoM,
    }


class template_task(orm.Model):
    _name = 'template.task'
    _description = "Task Template"

    _columns = {
        'name': fields.char('Task Summary', size=128, required=True, select=True),
        'planned_hours': fields.float('Planned Hours', help='Estimated time to do the task, usually set by the project manager when the task is in draft state.'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'user_id': fields.many2one('res.users', 'Task owner User')
    }


class sale_order_task_matrix(orm.Model):
    _name = 'sale.order.task.matrix'
    _description = "Matrix Sale to Task"

    _columns = {
        'sale_order_field_id': fields.many2one('ir.model.fields', 'Field From Sale Order', domain=[('model', '=', 'sale.order')]),
        'sale_order_line_field_id': fields.many2one('ir.model.fields', 'Field From Sale Order Line', domain=[('model', '=', 'sale.order.line')]),
        'task_field_id': fields.many2one('ir.model.fields', 'Field To Task', domain=[('model', '=', 'project.task')], required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
