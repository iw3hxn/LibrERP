# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2013 Didotech Srl. (<http://www.didotech.com>)
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


class project_task(orm.Model):

    _inherit = 'project.task'
    _order = 'date_deadline asc, priority asc, partner_id'
    
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            if record.project_id:
                name = record.project_id.name[:30] + ' : ' + record.name
            else:
                name = record.name
            if len(name) > 65:
                name = name[:65] + '...'
            res.append((record.id, name))
        return res
