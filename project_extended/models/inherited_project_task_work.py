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


class project_task_work(orm.Model):
    _inherit = 'project.task.work'

    def _get_project_task(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        task_work_ids = self.pool['project.task.work'].search(cr, uid, [('task_id', 'in', ids)], context=context)
        for task_work_id in task_work_ids:
            result[task_work_id] = True
        return result.keys()

    _columns = {
        'project_id': fields.related('task_id', 'project_id', type='many2one', relation='project.project', string="Project", store={
            'project.task.work': (lambda self, cr, uid, ids, c={}: ids, ['task_id'], 50),
            'project.task': (_get_project_task, ['project_id'], 20),
        }),
        'to_invoice': fields.related('task_id', 'project_id', 'to_invoice', type='many2one', relation='hr_timesheet_invoice.factor', string='Timesheet Invoicing Ratio')
    }
