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
from openerp.addons import base
from openerp.tools.translate import _


class project_project(orm.Model):
    _inherit = 'project.project'

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        project_id = super(project_project, self).create(cr, uid, vals, context)
        project = self.pool['project.project'].browse(cr, uid, project_id, context)
        
        if not project.partner_id and context.get('partner_id', False):
            self.pool['project.project'].write(cr, uid, project_id, {'partner_id': context['partner_id']}, context)

        if context.get('model', False) == 'sale.order':
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            name_prefix = context.get('name', vals.get('name', ''))
            if user.company_id.work_order_default_task_ids:
                task_obj = self.pool['project.task']
                for task in user.company_id.work_order_default_task_ids:
                    vals = {
                        'name': u"{0}: {1}".format(name_prefix, task.name),
                        'project_id': project_id,
                        'planned_hours': task.planned_hours,
                        'remaining_hours': task.planned_hours,
                        'user_id': task.user_id and task.user_id.id or False,
                    }
                    task_obj.create(cr, uid, vals, context)
                self.pool['project.project'].write(cr, uid, project_id, {'state': 'open'}, context)
        return project_id

    def _get_sale_order(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        sale_order_obj = self.pool['sale.order']
        for project in self.browse(cr, uid, ids, context):
            result[project.id] = sale_order_obj.search(cr, uid, [('project_id', '=', project.analytic_account_id.id)], context=context)
        return result

    _columns = {
        'sale_order_ids': fields.function(_get_sale_order, 'Sale Order', type='one2many', relation="sale.order",
                                      readonly=True, method=True),
    }
