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

from openerp.osv import orm, fields

class project_task(orm.Model):

    _inherit = "project.task"
    
    _columns = {
        'issue_ids': fields.one2many('project.issue', 'task_id', 'Issues', readonly=False),
    }


class project_issue(orm.Model):

    _inherit = "project.issue"

    _columns = {
        'work_ids': fields.one2many('project.task.work', 'issue_id', 'Work done'),
        'remaining_hours': fields.related('task_id', 'remaining_hours', type='float', string='Ore rimanenti'),
    }


#class project_task_work(orm.Model):

#    _inherit = "project.task.work"

#    _default = {
#        'task_id': lambda self, cr, uid, context: context.get('default_task_id', False),
#    }

