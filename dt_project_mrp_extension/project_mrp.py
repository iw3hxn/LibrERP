# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com) 
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
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

from osv import fields, osv
import netsvc


class project_project(osv.osv):
    _inherit = "project.project"
    _columns = {
        'procurement_ids': fields.one2many('procurement.order', 'project_id' ,'Procurement', ondelete='set null'),
    }

    def _validate_subflows(self, cr, uid, ids):
        for project in self.browse(cr, uid, ids):
            for proc in project.procurement_ids:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'procurement.order', proc.id, 'subflow.done', cr)

    def set_done(self, cr, uid, ids, *args, **kwargs):
        res = super(project_project, self).set_done(cr, uid, ids, *args, **kwargs)
        self._validate_subflows(cr, uid, ids)
        return res

    def set_cancel(self, cr, uid, ids, *args, **kwargs):
        res = super(project_project, self).set_cancel(cr, uid, ids, *args, **kwargs)
        self._validate_subflows(cr, uid, ids)
        return res

project_project()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
