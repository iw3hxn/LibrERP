# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
import openerp.tools as tools
import time


class Hr_Attendance(orm.Model):

    _inherit = "hr.attendance"

    def _get_date_tz(self, cr, uid, ids, field_names=None, arg=False, context={}):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        dt_format = tools.DEFAULT_SERVER_DATETIME_FORMAT
        tz = context.get('tz', 'UTC')
        for hr_attendance in self.browse(cr, uid, ids, context=context):
            res[hr_attendance.id] = hr_attendance.name and tools.server_to_local_timestamp(
                hr_attendance.name, dt_format, dt_format, tz) or False
        return res

    def _day_compute(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict.fromkeys(ids, '')
        for hr_attendance in self.browse(cr, uid, ids, context=context):
            res[hr_attendance.id] = time.strftime('%Y-%m-%d', time.strptime(hr_attendance.name_tz, '%Y-%m-%d %H:%M:%S'))
        return res

    _columns = {
        'name_tz': fields.function(_get_date_tz, method=True, type='char', string='Date with TZ', store={
            'hr.attendance': (lambda self, cr, uid, ids, c={}: ids, ['name'], 50)
        }),
        'day': fields.function(_day_compute, type='char', string='Day', select=1, size=32, store={
            'hr.attendance': (lambda self, cr, uid, ids, c={}: ids, ['name'], 100)
        }),
    }
