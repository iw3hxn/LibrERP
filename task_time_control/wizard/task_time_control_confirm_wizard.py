# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY
#    Pexego Sistemas Informáticos (http://www.pexego.es) All Rights Reserved
#    $Jesús Ventosinos Mayor$
#    $Javier Colmenero Fernández$
#    Copyright (c) 2014 Didotech srl (info at didotech.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
import time
from datetime import datetime


class task_time_control_confirm_wizard(orm.TransientModel):
    _name = 'task.time.control.confirm.wizard'

    def get_time(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if context.get('user_task_id', False):
            user_task = self.pool['time.control.user.task'].browse(cr, uid, context['user_task_id'], context)
            if user_task.work_start:
                start_datetime = datetime.strptime(user_task.work_start, '%Y-%m-%d %H:%M:%S.%f')
                # not possible to convert in DEFAULT_SERVER_DATETIME_FORMAT because there are also millisecond
            else:
                start_datetime = datetime.now()

            if user_task.work_end:
                end_datetime = datetime.strptime(user_task.work_end, '%Y-%m-%d %H:%M:%S.%f')
            else:
                end_datetime = datetime.now()
            end_seconds = time.mktime(end_datetime.timetuple())
            start_seconds = time.mktime(start_datetime.timetuple())
            diff_hours = (end_seconds - start_seconds) / 60 / 60

            return (user_task and diff_hours or 0.00)
        else:
            return 0.00

    def get_issue_ids(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        project_issue_obj = self.pool['project.issue']
        if context.get('user_task_id', False):
            user_task = self.pool['time.control.user.task'].browse(cr, uid, context['user_task_id'], context)
            task_ids = project_issue_obj.search(cr, uid, [('task_id', '=', user_task.started_task.id), ('state', 'not in', ['done', 'cancel'])], context=context)
            return task_ids

        return []

    _columns = {
        'task_date': fields.datetime('Date', required=False),
        'task_to_start': fields.many2one('project.task', 'Task to init'),
        'user_task': fields.many2one('time.control.user.task', 'User task'),
        'started_task': fields.many2one('project.task', 'Started Task'),
        'name': fields.char('name', size=128),
        'time': fields.float('time'),
        'issue_ids': fields.many2many('project.issue', string='Issues', readonly=True),
        'issue_id': fields.many2one('project.issue', 'Issue', domain="[('id', 'in', issue_ids[0][2])]"),
    }

    _defaults = {
        'time': get_time,
        'issue_ids': get_issue_ids,
        'task_date': lambda self, cr, uid, context: fields.date.context_today(cr, uid, context),
    }

    def close_confirm(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        user_task_obj = self.pool['time.control.user.task']
        project_task_obj = self.pool['project.task']

        wizard = self.browse(cr, uid, ids[0], context)
        user_task = wizard.user_task
        started_task = user_task.started_task

        if started_task:
            if user_task.work_start:
                start_datetime = datetime.strptime(user_task.work_start, '%Y-%m-%d %H:%M:%S.%f')
            else:
                start_datetime = datetime.now()
            if user_task.work_end:
                end_datetime = datetime.strptime(user_task.work_end, '%Y-%m-%d %H:%M:%S.%f')
            else:
                end_datetime = datetime.now()

            project_task_work_vals = {
                'name': wizard.name,
                'date': wizard.task_date or end_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                'task_id': started_task.id,
                'issue_id': wizard.issue_id and wizard.issue_id.id,
                'hours': wizard.time,
                'user_id': uid,
                'company_id': started_task.company_id and started_task.company_id.id or False,
                'work_start': start_datetime,
                'work_end': end_datetime
            }

            self.pool['project.task.work'].create(cr, uid, project_task_work_vals, context)

            user_task_obj.write(cr, uid, user_task.id, {'work_start': None, 'work_end': None, 'started_task': None}, context)

            count_other_users_in_task = user_task_obj.search(cr, uid, [('started_task', '=', started_task.id)], count=True, context=context)
            if count_other_users_in_task == 0:
                project_task_obj.write(cr, uid, started_task.id, {'state': 'open'}, context)

            if wizard.task_to_start.id:
                start_id = wizard.task_to_start.id
                if wizard.task_to_start.state == 'draft':
                    project_task_obj.do_open(cr, uid, start_id, context)
                project_task_obj.write(cr, uid, start_id, {'state': 'working'}, context)
                user_task_obj.write(cr, uid, user_task.id, {'work_start': end_datetime, 'started_task': start_id}, context)

        if wizard.issue_id:
            self.pool['project.issue'].case_close(cr, uid, [wizard.issue_id.id], (context,))

        return {'type': 'ir.actions.act_window_close'}
