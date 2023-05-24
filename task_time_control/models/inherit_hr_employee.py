# -*- coding: utf-8 -*-
##############################################################################

import logging
from datetime import datetime

import tools

from openerp.osv import orm

_logger = logging.getLogger(__name__)


class HrEmployee(orm.Model):
    _inherit = "hr.employee"

    def attendance_action_change(self, cr, uid, ids, ttype='action', context=None, dt=False, *args):
        res = super(HrEmployee, self).attendance_action_change(cr, uid, ids, ttype, context, dt, *args)
        if ttype == 'sign_out':
            time_control_model = self.pool['time.control.user.task']
            _logger.info("attendance_action_change ttype == 'sign_out'")
            task_ids = self.pool['project.task'].search(cr, uid, [('state', '=', 'working')], context=context)
            _logger.info("attendance_action_change task in state working ='{}'".format(task_ids))
            for employee in self.pool['hr.employee'].browse(cr, uid, ids, context):
                _logger.info("attendance_action_change employee='{}'".format(employee.name))
                time_control_ids = time_control_model.search(cr, uid, [('user', '=', employee.user_id.id), ('started_task', 'in', task_ids)], context=context)
                _logger.info("attendance_action_change find task working by employee='{}'".format(time_control_ids))
                for time_control in time_control_model.browse(cr, uid, time_control_ids, context):
                    if time_control.work_start:
                        start_datetime = datetime.strptime(time_control.work_start, '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        start_datetime = datetime.now()

                    end_datetime = datetime.now()
                    hours = (end_datetime - start_datetime).seconds / 60.0 / 60.0
                    end_datetime = end_datetime.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
                    start_datetime = start_datetime.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
                    project_task_work_vals = {
                        'name': "",
                        'date': end_datetime,
                        'task_id': time_control.started_task.id,
                        'issue_id': False,
                        'hours': hours,
                        'user_id': employee.user_id.id,
                        'company_id': employee.company_id and employee.company_id.id or False,
                        'work_start': start_datetime,
                        'work_end': end_datetime
                    }
                    self.pool['project.task.work'].create(cr, uid, project_task_work_vals, context)
                    time_control.write({'work_start': None, 'work_end': None, 'started_task': None})
                    time_control.started_task.write({'state': 'open'})

        return res
    #
    #
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     if context.get('no_create', False):
    #         raise orm.except_orm(
    #             'Errore',
    #             _('It is not allowed to create project from here'))
    #     return super(ProjectProject, self).create(cr, uid, values, context)
