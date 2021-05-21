# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Dhaval Patel (dhpatel82 at gmail.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import time
from openerp.osv import orm, fields


class HrDocumentCreation(orm.TransientModel):
    _name = 'hr.document.creation'
    _inherit = "hr.document.abstract"

    _columns = {
        'hr_employee_ids': fields.many2many('hr.employee', string="Employees", required=False),
    }

    def create_document(self, cr, uid, ids, context=None):
        context = context or self.context_get(cr, uid)
        hr_document_model = self.pool['hr.document']
        mod_model = self.pool['ir.model.data']
        act_model = self.pool['ir.actions.act_window']

        document_ids = []
        res = self.read(cr, uid, ids, ['hr_employee_ids'], context=context)
        res = res and res[0] or {}
        copy_data = self.copy_data(cr, uid, ids[0], context=context)
        del copy_data['hr_employee_ids']
        for employee_id in res['hr_employee_ids']:
            hr_document_value = copy_data.copy()
            hr_document_value['employee_id'] = employee_id
            doc_id = hr_document_model.create(cr, uid, hr_document_value, context)
            document_ids.append(doc_id)

        result = mod_model.get_object_reference(cr, uid, 'hr_document', 'open_module_tree_document')
        id = result and result[1] or False
        result = act_model.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in',[" + ','.join(map(str, document_ids)) + "])]"

        return result



