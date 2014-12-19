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


class project_project(orm.Model):
    _inherit = 'project.project'

    def create(self, cr, uid, vals, context=None):
        project_id = super(project_project, self).create(cr, uid, vals, context)
        project = self.pool['project.project'].browse(cr, uid, project_id)
        
        if not project.partner_id and context.get('partner_id', False):
            self.pool['project.project'].write(cr, uid, project_id, {'partner_id': context['partner_id']})

        if context.get('model', False) == 'sale.order':
            user = self.pool['res.users'].browse(cr, uid, uid)
            name_prefix = context.get('name', vals.get('name', ''))
            if user.company_id.work_order_default_task_ids:
                task_obj = self.pool['project.task']
                for task in user.company_id.work_order_default_task_ids:
                    task_obj.create(cr, uid, {
                        'name': u"{0}: {1}".format(name_prefix, task.name),
                        'project_id': project_id,
                        'planned_hours': task.planned_hours,
                        'remaining_hours': task.planned_hours
                    })
                self.pool['project.project'].write(cr, uid, project_id, {'state' : 'open'})
        return project_id


class project_task(orm.Model):
    _inherit = 'project.task'
    
    columns = {
        'ref': fields.reference('Reference', selection=base.res.res_request._links_get, size=None),
    }
