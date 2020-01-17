# -*- encoding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def _check_vat_readonly(self, cr, uid, ids, field_name, arg, context):
        """
            this method reads from system parameters the value from the key 'vatcf_minutes_amount_readonly'
            if the value exists uses the minutes given to calculate if the vat must be in readonly mode
            so the user can't modify the value of VAT
            if the user has a group 'Configuration' he CAN always modifies the value of the VAT

        """
        results = {}

        # return the value or False
        minutes_str = self.pool['ir.config_parameter'].get_param(cr, uid, 'vatcf_minutes_amount_readonly')

        if minutes_str:
            minutes_amount = int(minutes_str)
        else:
            minutes_amount = 0

        # boolean True or False
        has_group = self.pool['res.users'].has_group(cr, uid, 'base.group_system')

        for partner in self.browse(cr, uid, ids, context):

            results[partner.id] = True

            if minutes_amount and minutes_amount > 0:
                time_right_now = datetime.now()
                time_from_last_update = partner.write_date and (datetime.strptime(partner.write_date, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=minutes_amount)) or time_right_now
                delta_left = time_from_last_update - time_right_now
                seconds_left = int(delta_left.total_seconds())

                if seconds_left > 0:
                    results[partner.id] = False

            if has_group:
                results[partner.id] = False

        return results

    _columns = {
        'vat_readonly': fields.function(_check_vat_readonly, method=True, type='boolean'),
        'write_date': fields.datetime(string='Write Date')
    }
