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

from osv import fields, osv
import time
from datetime import datetime


class task_time_control_confirm_wizard(osv.osv_memory):
    _name = 'task.time.control.confirm.wizard'

    def get_time(self, cr, uid, context=None):
        if context.get('user_task_id', False):
            user_task = self.pool.get('time.control.user.task').browse(cr, uid, context['user_task_id'], context)
            if user_task.work_start:
                start_datetime = datetime.strptime(user_task.work_start, '%Y-%m-%d %H:%M:%S.%f')
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

    _columns = {
        'task_to_start': fields.many2one('project.task', 'Task to init'),
        'user_task': fields.many2one('time.control.user.task', 'User task'),
        'started_task': fields.many2one('project.task', 'Started Task'),
        'name': fields.char('name', size=128),
        'time': fields.float('time')
    }

    _defaults = {
        'time': get_time,
    }

    def close_confirm(self, cr, uid, ids, context=None):
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

            self.pool["project.task.work"].create(cr, uid, {
                'name': wizard.name,
                'date': end_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                'task_id': started_task.id,
                'hours': wizard.time,
                'user_id': uid,
                'company_id': started_task.company_id and started_task.company_id.id or False,
                'work_start': start_datetime,
                'work_end': end_datetime
            })

            user_task_obj.write(cr, uid, user_task.id, {'work_start': None, 'work_end': None, 'started_task': None})

            count_other_users_in_task = user_task_obj.search(cr, uid, [('started_task', '=', started_task.id)], count=True)
            if count_other_users_in_task == 0:
                project_task_obj.write(cr, uid, started_task.id, {'state': 'open'})

            if wizard.task_to_start.id:
                start_id = wizard.task_to_start.id
                if wizard.task_to_start.state == 'draft':
                    project_task_obj.do_open(cr, uid, start_id, context)
                project_task_obj.write(cr, uid, start_id, {'state': 'working'})
                user_task_obj.write(cr, uid, user_task.id, {'work_start': end_datetime, 'started_task': start_id})
        return {'type': 'ir.actions.act_window_close'}
