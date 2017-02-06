# -*- encoding: utf-8 -*-

from openerp.osv import orm, fields
from openerp import SUPERUSER_ID


class hr_attendance(orm.Model):
    _inherit = 'hr.attendance'

    _columns = {
        'latitude': fields.float('Latitude', digits=(16, 4)),
        'longitude': fields.float('Longitude', digits=(16, 4)),
    }
