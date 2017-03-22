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


class project_issue(orm.Model):

    _inherit = "project.issue"

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        return [(x['id'], str(x.id)) for x in self.browse(cr, uid, ids, context=context)]

    def on_change_project(self, cr, uid, ids, project_id, context=None):
        if not project_id:
            return {'value': {}}

        project = self.pool['project.project'].browse(cr, uid, project_id, context=context)

        task_ids = self.pool['project.task'].search(cr, uid, [('project_id', '=', project_id), ('state', 'in', ['open', 'working'])], context=context, limit=1)
        if task_ids and len(task_ids) == 1:
            task_id = task_ids[0]
        else:
            task_id = False
        return {
            'value': {
                'partner_id': project.partner_id and project.partner_id.id,
                'task_id': task_id,
            }
        }

    _columns = {
        'work_ids': fields.one2many('project.task.work', 'issue_id', 'Work done'),
        'remaining_hours': fields.related('task_id', 'remaining_hours', type='float', string='Ore rimanenti'),
    }

    def case_close(self, cr, uid, ids, *args):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of case's Ids
        @param *args: Give Tuple Value
        """

        res = super(project_issue, self).case_close(cr, uid, ids, *args)
        import pdb;pdb.set_trace()
        return res


