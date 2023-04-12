# -*- coding: utf-8 -*-
##############################################################################

from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import orm, fields


class HrEmployee(orm.Model):
    _inherit = "hr.employee"

    def attendance_action_change(self, cr, uid, ids, ttype='action', context=None, dt=False, *args):
        res = super(HrEmployee, self).attendance_action_change(cr, uid, ids, ttype, context, dt, *args)
        if ttype == 'sign_out':
            time_control_model = self.pool['time.control.user.task']

            for employee in self.pool['hr.employee'].browse(cr, uid, ids, context):
                task_ids = self.pool['project.task'].search(cr, uid, [('state', '=', 'working')], context=context)
                time_control_ids = time_control_model.search(cr, uid, [('user', '=', employee.user_id.id), ('started_task', 'in', task_ids)], context=context)
                for time_control in time_control_model.browse(cr, uid, time_control_ids, context):
                    if time_control.work_start:
                        start_datetime = datetime.strptime(time_control.work_start, '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        start_datetime = datetime.now()

                    end_datetime = datetime.now()
                    hours = (end_datetime - start_datetime).seconds / 60.0 / 60.0
                    project_task_work_vals = {
                        'name': "",
                        'date': end_datetime.strftime('%d-%m-%Y %H:%M:%S'),
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

        return res
    #
    #
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     if context.get('no_create', False):
    #         raise orm.except_orm(
    #             'Errore',
    #             _('It is not allowed to create project from here'))
    #     return super(ProjectProject, self).create(cr, uid, values, context)
