# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2016 Didotech Srl. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################.

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID


class project_task(orm.Model):

    _inherit = 'project.task'
    _order = 'date_deadline asc, priority asc, partner_id'

    _group_by_full = {}
    
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if record.project_id:
                name = record.project_id.name[:30] + ' : ' + record.name
            else:
                name = record.name
            # if len(name) > 65:
            #     name = name[:65] + '...'
            res.append((record.id, name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):

        task_selection = super(project_task, self).name_search(cr, uid, name, args, operator, context=context, limit=limit)
        if name:
            project_ids = self.pool['project.project'].search(cr, uid, [('name', 'ilike', name)], context=context)
            if project_ids:
                if args:
                    relative_tasks = self.name_search(cr, uid, '', args + [('project_id', 'in', project_ids)], operator, context=context, limit=limit)
                else:
                    relative_tasks = self.name_search(cr, uid, '', [('project_id', 'in', project_ids)], operator, context=context, limit=limit)
                if relative_tasks:
                    task_selection = list(set(task_selection + relative_tasks))

        # Sort by name
        return sorted(task_selection, key=lambda x: x[1])

    _columns = {
        'project_id': fields.many2one('project.project', 'Project', ondelete='set null', select="1", required=True),
    }

    # def do_open(self, cr, uid, ids, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid, context)
    #     for task in self.browse(cr, uid, ids, context):
    #         for parent_task in task.parent_ids:
    #             if parent_task.state != 'new':
    #                 raise orm.except_orm(_('Error!'), _("You can start only task with closed delegated"))
    #     return super(project_task, self).do_open(cr, uid, ids, context)

    def onchange_project(self, cr, uid, id, project_id):
        context = self.pool['res.users'].context_get(cr, uid)
        res = super(project_task, self).onchange_project(cr, uid, id, project_id)
        if project_id:
            project = self.pool['project.project'].browse(cr, uid, project_id, context)
            user_id = [x.id for x in project.members]
            if res.get('value', False):
                res['value'].update({'other_users_ids': [(6, 0, user_id)]})
        return res

    # def fields_get(self, cr, uid, allfields=None, context=None):
    #     if context is None:
    #         context = self.pool['res.users'].context_get(cr, uid, context=context)
    #     # context.update({
    #     #     'nodelete': '1', 'nocreate': '1', 'noduplicate': '1'
    #     # })
    #     ret = super(project_task, self).fields_get(cr, uid, allfields=allfields, context=context)
    #
    #     group_obj = self.pool['res.groups']
    #     is_project_user = group_obj.user_in_group(cr, uid, uid, 'project.group_project_user', context=context)
    #     is_project_manager = group_obj.user_in_group(cr, uid, uid, 'project.group_project_manager', context=context)
    #     if is_project_user and not is_project_manager:
    #         if 'partner_id' in ret:
    #             ret['partner_id']['readonly'] = 1
    #         if 'sequence' in ret:
    #             ret['sequence']['readonly'] = 1
    #     if 'planned_hours' in ret:
    #         ret['planned_hours']['readonly'] = 1
    #     if 'remaining_hours' in ret:
    #         ret['remaining_hours']['readonly'] = 1
    #     return ret
