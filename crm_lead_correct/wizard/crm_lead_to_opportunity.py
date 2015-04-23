# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import orm, fields
from tools.translate import _
import vatnumber


class crm_lead2opportunity_partner(orm.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    _columns = {
        'vat': fields.char('VAT', size=64, readonly=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        """
            Default get for name, opportunity_ids
            if there is an exisitng  partner link to the lead, find all existing opportunity link with this partnet to merge
            all information together
        """
        lead_obj = self.pool['crm.lead']
        res = super(crm_lead2opportunity_partner, self).default_get(cr, uid, fields, context=context)
        for lead in lead_obj.browse(cr, uid, context.get('active_ids')):
            if lead.vat:
                if vatnumber.check_vat(lead.vat):
                    res['vat'] = lead.vat
                    partner_ids = self.pool['res.partner'].search(cr, uid, [('vat', 'ilike', lead.vat)], context=context)
                    if partner_ids:
                        partner = self.pool['res.partner'].browse(cr, uid, partner_ids[0], context=context)
                        res['partner_id'] = partner.id
                        res['action'] = 'exist'
                else:
                    raise orm.except_orm(_('Error :'), _("VAT '%s' not valid.") % lead.vat)
        return res

