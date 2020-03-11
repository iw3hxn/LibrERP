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
        'action': fields.selection([('exist', 'Link to an existing partner'), \
                                    ('create', 'Create a new partner')], \
                                    'Related Partner', required=True),
        'vat': fields.char('VAT', size=64, readonly=True),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
    }

    def on_change_city(self, cr, uid, ids, city, zip_code=None):
        return self.pool['res.partner.address'].on_change_city(cr, uid, ids, city, zip_code)

    def on_change_zip(self, cr, uid, ids, zip_code):
        return self.pool['res.partner.address'].on_change_zip(cr, uid, ids, zip_code)

    def default_get(self, cr, uid, fields, context=None):
        """
            Default get for name, opportunity_ids
            if there is an exisitng  partner link to the lead, find all existing opportunity link with this partnet to merge
            all information together
        """
        lead_obj = self.pool['crm.lead']
        res = super(crm_lead2opportunity_partner, self).default_get(cr, uid, fields, context=context)
        for lead in lead_obj.browse(cr, uid, context.get('active_ids'), context=context):
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
            res.update({
                'street': lead.street or '',
                'street2': lead.street2 or '',
                'zip': lead.zip or '',
                'city': lead.city or '',
            })
        return res

    def action_apply(self, cr, uid, ids, context=None):
        """
        This converts lead to opportunity and opens Opportunity view
        """
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        lead_obj = self.pool['crm.lead']
        lead_ids = context.get('active_ids', [])

        lead = self.browse(cr, uid, ids, context)[0]

        vals = {
            'street': lead.street or '',
            'street2': lead.street2 or '',
            'zip': lead.zip or '',
            'city': lead.city or '',
        }
        lead_obj.write(cr, uid, lead_ids, vals, context=context)
        res = super(crm_lead2opportunity_partner, self).action_apply(cr, uid, ids, context=context)
        return res
    #
    # def _create_partner(self, cr, uid, ids, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     partner_ids = super(crm_lead2opportunity_partner, self)._create_partner(cr, uid, ids, context)
    #     rec_ids = context and context.get('active_ids', [])
    #     lead_obj = self.pool['crm.lead']
    #     contact_obj = self.pool['res.partner.address.contact']
    #     for data in self.browse(cr, uid, ids, context=context):
    #         for lead in lead_obj.browse(cr, uid, rec_ids, context=context):
    #             if data.action == 'create':
    #                 if lead.partner_address_id:
    #                     lead.partner_address_id.write({'name': False})
    #                     if lead.contact_name:
    #                         contact_id = contact_obj.create(cr, uid, {
    #                             'last_name': lead.contact_name[0:lead.contact_name.find(' ')],
    #                             'first_name': lead.contact_name[lead.contact_name.find(' '):],
    #                             'title': lead.title.id,
    #                             'email': lead.email_from,
    #                             'website': lead.website,
    #                             'address_id': lead.partner_address_id.id,
    #                             'function_id': lead.function_id and lead.function_id.id or False,
    #                             'mobile': lead.mobile or lead.phone,
    #                         })
    #                         lead.write({'contact_id': contact_id})
    #                     else:
    #                         raise orm.except_orm(_('Error!'), _("Missing Contact Name"))
    #     return partner_ids
