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


class crm_meeting_by_province(orm.TransientModel):
    _name = 'crm.meeting.by.province'
    _description = 'Print Zone wise Report'
    _columns = {
        'date_from': fields.date("Start Date"),
        'date_to': fields.date("End Date"),
        "province": fields.many2one("res.province", "Province"),
    }

    _defaults = {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_from', 'date_to', 'province'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        datas['form']['ids'] = context.get('active_ids', [])
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'crm.meeting.province',
            'datas': datas,
        }
