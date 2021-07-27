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
from openerp import SUPERUSER_ID


class ProjectProject(orm.Model):
    _inherit = "project.project"

    def _open_ticket(self, cr, uid, ids, field_name, arg, context=None):
        if not len(ids):
            return []
        '''
        Show if have or not a bom
        '''
        context = context or self.pool['res.users'].context_get(cr, uid)

        project_issue_obj = self.pool['project.issue']

        res = {}
        ids = ids or []

        for project_id in ids:
            task_ids = project_issue_obj.search(cr, SUPERUSER_ID, [('project_id', '=', project_id), ('state', 'not in', ['done', 'cancel'])], context=context, count=True)
            res[project_id] = task_ids

        return res
    
    _columns = {
        'issue_ids': fields.one2many('project.issue', 'project_id', 'Issues', readonly=True),
        'open_issue': fields.function(_open_ticket, method=True, type="integer", string="Open Ticket"),
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        default.update({
            'issue_ids': False,
        })
        res_id = super(ProjectProject, self).copy(cr, uid, ids, default, context)
        return res_id


