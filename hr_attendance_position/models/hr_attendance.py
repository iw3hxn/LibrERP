# -*- coding: utf-8 -*-
# © 2017-2018 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from tools.translate import _


class hr_attendance(orm.Model):
    _inherit = 'hr.attendance'

    def _get_position(self, cr, uid, ids, field_name, arg, context):
        address_model = self.pool['res.partner.address']

        # 0.001 - 111.12 m
        # delta = 0.0010
        delta = float(self.pool['ir.config_parameter'].get_param(
            cr,
            uid,
            'gps_coordinate_compare_delta',
            default=0.001
        ))

        positions = {}

        for attendance in self.browse(cr, uid, ids, context):
            address_ids = address_model.search(cr, uid, [
                ('latitude', '>=', attendance.latitude - delta),
                ('latitude', '<=', attendance.latitude + delta),
                ('longitude', '>=', attendance.longitude - delta),
                ('longitude', '<=', attendance.longitude + delta),
            ])

            if address_ids:
                addresses = address_model.browse(cr, uid, address_ids, context)
                addresses = [address.partner_id.name for address in addresses]
                positions[attendance.id] = ', \n'.join(addresses)
            else:
                positions[attendance.id] = False

        return positions

    _columns = {
        'latitude': fields.float('Latitude', digits=(16, 4)),
        'longitude': fields.float('Longitude', digits=(16, 4)),
        'position': fields.function(_get_position, string=_('Position'), method=True, type='text')
    }

    def action_create_relation(self, cr, uid, ids, context):
        view = self.pool['ir.model.data'].get_object_reference(cr, uid,
            'hr_attendance_position', 'wizard_set_partner_position_form')
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Set position'),
            'res_model': 'wizard.set.partner.position',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new'
        }
