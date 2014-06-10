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
    
    _columns = {
        'delivery_note_journal_id': fields.many2one('account.analytic.journal', 'Delivery Note Journal'),
        'expense_journal_id': fields.many2one('account.analytic.journal', 'Expense Journal'),
        'work_order_default_task_ids': fields.one2many('template.task', 'company_id', string='Default Work Order Tasks'),
        'hour': fields.many2one('product.uom', 'Hour UoM', required=True)
    }


class template_task(orm.Model):
    _name = 'template.task'
    
    _columns = {
        'name': fields.char('Task Summary', size=128, required=True, select=True),
        'planned_hours': fields.float('Planned Hours', help='Estimated time to do the task, usually set by the project manager when the task is in draft state.'),
        'company_id': fields.many2one('res.company', 'Company', required=True)
    }
