# -*- encoding: utf-8 -*-

from openerp.osv import orm, fields
from math import radians, cos, sin, asin, sqrt
from openerp import SUPERUSER_ID


class hr_employee(orm.Model):
    _inherit = 'hr.employee'

    def _get_employee(self, cr, uid, context):
        employee_id = self.pool['hr.sign.in.out']._get_empid(cr, uid, context=context)
        return employee_id

    def _get_employee_id(self, cr, uid, context):
        employee_id = self.pool['hr.sign.in.out']._get_empid(cr, uid, context=context).get('emp_id')
        return employee_id

    def telegram_attendance_action(self, cr, uid, position, employee_id, type, context=None):
        hr_attendance_id = self.pool['hr.employee'].attendance_action_change(cr, uid, [employee_id], type, context)
        if hr_attendance_id and isinstance(position, (list, tuple)):
            self.pool['hr.attendance'].write(cr, uid, hr_attendance_id, {
                'latitude': position[0],
                'longitude': position[1]},
                context)

        return hr_attendance_id

    def telegram_sign_in(self, cr, uid, context=None):
        context = context or self.context_get(cr, uid)
        emp_id = self._get_employee_id(cr, uid, context)
        if emp_id:
            att_obj = self.pool['hr.attendance']
            att_id = att_obj.search(cr, uid, [('employee_id', '=', emp_id)], limit=1, order='name desc')
            last_att = att_obj.browse(cr, uid, att_id, context=context)
            if last_att:
                last_att = last_att[0]

            cond = not last_att or last_att.action == 'sign_out'
            if cond:
                position = self.pool['res.users'].get_position(cr, uid, cancel_data=True, context=context)
                self.telegram_attendance_action(cr, uid, position, emp_id, 'sign_in', context)
                return True
        return False

    def telegram_sign_out(self, cr, uid, context=None):
        context = context or self.context_get(cr, uid)
        emp_id = self._get_employee_id(cr, uid, context)
        if emp_id:
            att_obj = self.pool['hr.attendance']
            att_id = att_obj.search(cr, uid, [('employee_id', '=', emp_id)], limit=1, order='name desc')
            last_att = att_obj.browse(cr, uid, att_id, context=context)
            if last_att:
                last_att = last_att[0]

            cond = not last_att or last_att.action == 'sign_in'
            if cond:
                position = self.pool['res.users'].get_position(cr, uid, cancel_data=True, context=context)
                self.telegram_attendance_action(cr, uid, position, emp_id, 'sign_out', context)
                return True
        return False

    def get_coordinates_distance(self, point1, point2):
        """
            Calculate the great circle distance between two points on the earth (specified in decimal degrees)
            6367 earth radius
        """
        lon1 = point1[0]
        lat1 = point1[1]
        lon2 = point2[0]
        lat2 = point2[1]

        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6367 * c
        return km
