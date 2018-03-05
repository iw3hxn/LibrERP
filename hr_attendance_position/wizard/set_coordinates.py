# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class WizardSetPartnerPosition(orm.TransientModel):
    _name = 'wizard.set.partner.position'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'address_id': fields.many2one('res.partner.address', 'Address', required=True)
    }

    def action_set_position(self, cr, uid, wizard_ids, context):
        active_id = context['active_id']
        if active_id and wizard_ids:
            wizard = self.browse(cr, uid, wizard_ids[0], context)
            attendance = self.pool['hr.attendance'].browse(cr, uid, active_id, context)

            wizard.address_id.write({
                'latitude': attendance.latitude,
                'longitude': attendance.longitude
            })

        return {
            'type': 'ir.actions.act_window_close',
        }
