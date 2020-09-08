# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU AfferoGeneral Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re
import time
from datetime import datetime

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


class ProjectIssue(orm.Model):

    _inherit = "project.issue"
    _description = "Project Issue"
    _order = "priority, ordering_date desc nulls last, create_date desc"

    def on_change_project(self, cr, uid, ids, project_id, email_from, context=None):
        if not project_id or not ids:
            return {'value': {}}

        context = context or self.pool['res.users'].context_get(cr, uid)

        if isinstance(ids, (int, long)):
            ids = [ids]

        project = self.pool['project.project'].browse(cr, uid, project_id, context=context)

        task_ids = self.pool['project.task'].search(cr, uid, [('project_id', '=', project_id), ('state', 'in', ['open', 'working'])], context=context, limit=1)
        if task_ids and len(task_ids) == 1:
            task_id = task_ids[0]
        else:
            task_id = False

        vals = {
            'partner_id': project.partner_id and project.partner_id.id or False,
            'task_id': task_id,
            'analytic_account_id': project.analytic_account_id.id,
        }
        issue = self.browse(cr, uid, ids[0], context)
        if not issue.user_id:
            vals['user_id'] = uid

        return {
            'value': vals
        }

    def onchange_task_id(self, cr, uid, ids, task_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(ProjectIssue, self).onchange_task_id(cr, uid, ids, task_id, context)
        if not res.get('value', {}).get('user_id', False):
            issue = self.browse(cr, uid, ids[0], context)
            if not issue.user_id:
                res['value']['user_id'] = uid
        return res

    def case_close(self, cr, uid, ids, *args):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of case's Ids
        @param *args: Give Tuple Value

        """
        res = super(ProjectIssue, self).case_close(cr, uid, ids, *args)
        context = self.pool['res.users'].context_get(cr, uid)
        for issue in self.browse(cr, uid, ids, context):
            if not issue.task_id:
                raise orm.except_orm(
                    _(u'Error'),
                    _(u'You have to set task'))

            if issue.project_id and issue.user_id:
                if issue.date_open and (issue.date_open != issue.date_closed):
                    start_datetime = datetime.strptime(issue.date_open, DEFAULT_SERVER_DATETIME_FORMAT)
                    end_datetime = datetime.strptime(issue.date_closed, DEFAULT_SERVER_DATETIME_FORMAT)
                    end_seconds = time.mktime(end_datetime.timetuple())
                    start_seconds = time.mktime(start_datetime.timetuple())
                    diff_hours = (end_seconds - start_seconds) / 60 / 60
                else:
                    diff_hours = 0.16
                task_vals = {
                    'date': issue.date_closed,
                    'task_id': issue.task_id.id,
                    'hours': diff_hours,
                    'user_id': issue.user_id.id,
                    'name': u'[{issue_id}] Ticket {name}'.format(issue_id=issue.id, name=issue.name),
                    'issue_id': issue.id
                }
                self.pool['project.task.work'].create(cr, uid, task_vals, context)
        return res

    def create(self, cr, uid, vals, context):
        if not vals.get('project_id', False):
            if vals.get('email_from'):
                contact_obj = self.pool['res.partner.address.contact']
                project_obj = self.pool['project.project']
                task_obj = self.pool['project.task']
                email_from = re.findall(r'([^ ,<@]+@[^> ,]+)', vals.get('email_from'))
                for email in email_from:
                    contact_ids = contact_obj.search(cr, uid, [('email', '=', email)], context=context)
                    if contact_ids:
                        partner_id = contact_obj.browse(cr, uid, contact_ids, context)[0].partner_id.id
                        project_ids = project_obj.search(cr, uid, [
                            ('partner_id', '=', partner_id),
                            ('state', 'in', ['open'])
                        ], context=context)
                        if project_ids and len(project_ids) == 1:
                            task_ids = task_obj.search(cr, uid, [
                                ('project_id', '=', project_ids[0]),
                                ('state', 'in', ['open', 'working'])
                            ], context=context)
                            if task_ids and len(task_ids) == 1:
                                task_id = task_ids[0]
                                user = task_obj.browse(cr, uid, [task_id], context)[0].user_id
                                vals.update({
                                    'partner_id': partner_id,
                                    'project_id': project_ids[0],
                                    'task_id': task_id,
                                    'user_id': user and user.id or False
                                })
                            else:
                                user = project_obj.browse(cr, uid, project_ids, context)[0].user_id
                                vals.update({
                                    'partner_id': partner_id,
                                    'project_id': project_ids[0],
                                    'user_id': user and user.id or False
                                })

        res = super(ProjectIssue, self).create(cr, uid, vals, context)
        return res

    def silent_done(self, cr, uid, context=None):

        if context.get('active_id'):
            # Context that disable base.action.rule
            new_context = {'action': True, '_action_trigger': 'write'}
            self.write(cr, uid, context['active_id'], {'state': 'done'}, new_context)
        # end if

        return True
    # end silent_done

    def _get_ordering_date(self, cr, uid, ids, field_name, arg, context):

        result = dict()

        for record_id in ids:
            current_issue = self.pool['project.issue'].browse(cr, uid, ids, context=context)[0]
            result[record_id] = current_issue.write_date or current_issue.create_date
        # end for

        return result
    # end _get_ordering_date

    # def name_get(self, cr, uid, ids, context=None):
    #     if not ids:
    #         return []
    #     if isinstance(ids, (int, long)):
    #         ids = [ids]
    #     return [(x['id'], str(x.id)) for x in self.browse(cr, uid, ids, context=context)]

    # def case_close(self, cr, uid, ids, *args):
    #     """
    #     @param self: The object pointer
    #     @param cr: the current row, from the database cursor,
    #     @param uid: the current user’s ID for security checks,
    #     @param ids: List of case's Ids
    #     @param *args: Give Tuple Value
    #     """
    #
    #     res = super(ProjectIssue, self).case_close(cr, uid, ids, *args)
    #     # import pdb;pdb.set_trace()
    #     return res

    _columns = {
        'work_ids': fields.one2many('project.task.work', 'issue_id', 'Work done'),
        'remaining_hours': fields.related('task_id', 'remaining_hours', type='float', string='Ore rimanenti'),
        'status_id': fields.many2one(obj='project.issue.status', string='Status', required=False),
        'ordering_date': fields.function(
            _get_ordering_date,
            type='datetime',
            method=True,
            string='Update Date',
            readonly=True,
            store=True
        ),
    }
# end ProjectIssue
