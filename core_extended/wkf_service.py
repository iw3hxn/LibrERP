# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.workflow import wkf_service
from openerp.osv import orm
from openerp.tools.translate import _


class workflow_service(wkf_service.workflow_service):
    def __init__(self, *args, **kw):
        super(workflow_service, self).__init__(*args, **kw)

    def trg_last_action(self, uid, model, obj_id, cr):
        """
            This function returns information about last workflow activity
        """

        cr.execute("SELECT * FROM wkf_instance WHERE res_id=%s AND res_type=%s", (obj_id, model))
        rows = cr.fetchall()

        if len(rows) > 1:
            raise orm.except_orm(_('Warning'), _('wkf_instance: More than one result returned...'))

        inst_id, wkf_id, uid, res_id, res_type, state = rows[0]

        cr.execute("SELECT act_id, inst_id, state FROM wkf_workitem WHERE inst_id=%s ORDER BY id DESC", (inst_id, ))
        rows = cr.fetchall()

        if len(rows) > 1:
            print 'act_id, inst_id, state'
            for row in rows:
                print row[0], row[1], row[2]
        #     raise orm.except_orm(_('Warning'), _('wkf_workitem: More than one result returned for inst_id "{}"...'.format(inst_id)))

        act_id, inst_id, state = rows[0]

        cr.execute("SELECT id, wkf_id, name, action FROM wkf_activity WHERE id=%s ORDER BY id", (act_id, ))
        rows = cr.fetchall()

        if len(rows) > 1:
            raise orm.except_orm(_('Warning'), _('wkf_activity: More than one result returned...'))

        return dict(zip(('wkf_activity_id', 'wkf_instance_id', 'name', 'action'), rows[0]))

workflow_service()
