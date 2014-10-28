# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2014 Didotech SRL (info at didotech.com)
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

from openerp.osv import orm, fields
import crm
from mail.mail_message import to_email


COLOR_SELECTION = [
    ('aqua', u"Aqua"),
    ('black', u"Black"),
    ('blue', u"Blue"),
    ('brown', u"Brown"),
    ('cadetblue', u"Cadet Blue"),
    ('darkblue', u"Dark Blue"),
    ('fuchsia', u"Fuchsia"),
    ('forestgreen', u"Forest Green"),
    ('green', u"Green"),
    ('grey', u"Grey"),
    ('red', u"Red"),
    ('orange', u"Orange")
]


class crm_lead_correct(crm.crm_lead.crm_case, orm.Model):
    _inherit = 'crm.lead'

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        leads = self.browse(cr, uid, ids)
        for lead in leads:
            if lead.categ_id:
                value[lead.id] = lead.categ_id.color
            else:
                value[lead.id] = 'black'

        return value
   
    def _get_sale_order(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        crm_lead_obj = self.pool['crm.lead']
        sale_order_obj = self.pool['sale.order']
        
        for crm_lead in crm_lead_obj.browse(cr, uid, ids, context):
            partner_id = crm_lead.partner_id.id
            contact_id = crm_lead.partner_address_id.id
            if contact_id:
                result[crm_lead.id] = sale_order_obj.search(cr, uid, [('partner_id', '=', partner_id), ('partner_order_id', '=', contact_id)])
            else:
                result[crm_lead.id] = sale_order_obj.search(cr, uid, [('partner_id', '=', partner_id)])
        return result
    
    def _get_crm_lead(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        crm_lead_obj = self.pool['crm.lead']
        for crm_lead in crm_lead_obj.browse(cr, uid, ids, context):
            name = crm_lead.name
            partner_id = crm_lead.partner_id.id
            contact_id = crm_lead.partner_address_id.id
            if contact_id:
                result[crm_lead.id] = crm_lead_obj.search(cr, uid, [('partner_id', '=', partner_id), ('partner_address_id', '=', contact_id), ('name', '!=', name)])
            else:
                result[crm_lead.id] = crm_lead_obj.search(cr, uid, [('partner_id', '=', partner_id), ('name', '!=', name)])
        return result

    _columns = {
        'province': fields.many2one('res.province', string='Province', ondelete='restrict'),
        'region': fields.many2one('res.region', string='Region', ondelete='restrict'),
        'find_city': fields.boolean('Find City'),
        'website': fields.char('Website', size=64, help="Website of Partner."),
        'function_id': fields.many2one('res.contact.function', 'Function'),
        'phonecall_ids': fields.one2many('crm.phonecall', 'opportunity_id', 'Phonecalls'),
        'meeting_ids': fields.one2many('crm.meeting', 'opportunity_id', 'Meetings'),
        'partner_category_id': fields.many2one('res.partner.category', 'Partner Category'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True),
        'sale_order': fields.function(_get_sale_order, 'Sale Order', type='one2many', relation="sale.order", readonly=True, method=True),
        'crm_lead': fields.function(_get_crm_lead, 'Opportunity', type='one2many', relation="crm.lead", readonly=True, method=True)
    }

    _defaults = {
        'name': '/',
    }

    _order = "create_date desc"

    def _lead_create_partner(self, cr, uid, lead, context=None):

        partner_obj = self.pool['res.partner']
        partner_id = partner_obj.create(cr, uid, {
            'name': lead.partner_name or lead.contact_name or lead.name,
            'user_id': lead.user_id.id,
            'comment': lead.description,
            'website': lead.website,
            'section_id': lead.section_id.id or False,
            'address': [],
            'company_id': lead.company_id.id,
            'customer': False,
            'supplier': False,
            'category_id': lead.partner_category_id and [(6, 0, [lead.partner_category_id.id])]

        })
        #partner_obj.write(cr, uid, partner_id, {'customer': False})

        #import pdb
        #pdb.set_trace()
        #category_obj = self.pool['res.partner.category']
        #category_id = lead.partner_category_id.id
        #category_data = category_obj.browse(cr, uid, category_id)
        #if customer_id not in category_data['partner_ids']:
        #    category_data['partner_ids'].append(partner_id)
        #    category = category_obj.browse(cr, uid, category_id)
        #    category.partner_ids = [(6, 0, category_data['partner_ids'])]
        #    category_obj.write(cr, uid, category_id, category_data)

        return partner_id

    def _lead_create_partner_address(self, cr, uid, lead, partner_id, context=None):
        address = self.pool['res.partner.address']
        address_id = address.create(cr, uid, {
            'partner_id': partner_id,
            'name': lead.contact_name,
            'phone': lead.phone,
            'mobile': lead.mobile,
            'email': lead.email_from and to_email(lead.email_from)[0],
            'fax': lead.fax,
            'title': lead.title and lead.title.id or False,
            'function': lead.function_id and lead.function_id.name or False,
            'street': lead.street,
            'street2': lead.street2,
            'zip': lead.zip,
            'city': lead.city,
            'country_id': lead.country_id and lead.country_id.id or False,
            'state_id': lead.state_id and lead.state_id.id or False,
        })

        if lead.contact_name:
            vals = {
                'last_name': lead.contact_name[0:lead.contact_name.find(' ')],
                'first_name': lead.contact_name[lead.contact_name.find(' '):],
                'title': lead.title.id,
                'email': lead.email_from,
                'website': lead.website,
                'address_id': address_id,
                'function_id': lead.function_id and lead.function_id.id or False,
                'mobile': lead.mobile or lead.phone,
            }
            contact_partner_address_obj = self.pool['res.partner.address.contact']
            contact_partner_address_obj.create(cr, uid, vals, context)
        return address_id

    def on_change_city(self, cr, uid, ids, city, zip_code=None):
        return self.pool['res.partner.address'].on_change_city(cr, uid, ids, city, zip_code)

    def on_change_zip(self, cr, uid, ids, zip_code):
        return self.pool['res.partner.address'].on_change_zip(cr, uid, ids, zip_code)

    def on_change_province(self, cr, uid, ids, province):
        return self.pool['res.partner.address'].on_change_province(cr, uid, ids, province)

    def on_change_region(self, cr, uid, ids, region):
        return self.pool['res.partner.address'].on_change_region(cr, uid, ids, region)

    def check_address(self, cr, uid, ids, vals):
        address_obj = self.pool['res.partner.address']
        leads = self.browse(cr, uid, ids)

        for lead in leads:
            partner_vals = {}
            if lead.partner_id:
                if not lead.partner_id.email and vals.get('email_from', False):
                    partner_vals['email'] = vals['email_from']

                if not lead.partner_id.phone and not lead.partner_id.mobile and vals.get('phone', False):
                    partner_vals['phone'] = vals['phone']

                if partner_vals:
                    address_ids = address_obj.search(cr, uid, [
                        ('partner_id', '=', lead.partner_id.id), ('type', '=', 'default')])
                    if address_ids:
                        address_obj.write(cr, uid, address_ids[0], partner_vals)
                    else:
                        partner_vals['type'] = 'default'
                        partner_vals['partner_id'] = lead.partner_id.id
                        address_obj.create(cr, uid, partner_vals)
        return True

    def create(self, cr, uid, vals, context=None):
        vals = self.pool['res.partner.address']._set_vals_city_data(cr, uid, vals)

        if vals.get('name', '/') == '/':
            sequence_data_id = self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'crm_lead_correct', 'seq_lead_item')
            if sequence_data_id:
                new_name = self.pool['ir.sequence'].next_by_id(cr, uid, sequence_data_id[1], context=context)
                vals.update({'name': new_name})

        result = super(crm_lead_correct, self).create(cr, uid, vals, context=context)

        if vals.get('email_from', False) or vals.get('phone', False):
            self.check_address(cr, uid, [result], vals)

        return result

    def write(self, cr, uid, ids, vals, context=None):
        vals = self.pool['res.partner.address']._set_vals_city_data(cr, uid, vals)
        result = super(crm_lead_correct, self).write(cr, uid, ids, vals, context=context)

        if vals.get('email_from', False) or vals.get('phone', False):
            self.check_address(cr, uid, ids, vals)

        return result

    def copy(self, cr, uid, ids, defaults, context=None):
        defaults['name'] = '/'
        #defaults['type'] = 'lead'

        return super(crm_lead_correct, self).copy(cr, uid, ids, defaults, context)


class crm_phonecall(orm.Model):
    _inherit = 'crm.phonecall'

    def schedule_another_phonecall(self, cr, uid, ids, schedule_time, call_summary,
                                   user_id=False, section_id=False, categ_id=False, action='schedule', context=None):

        phonecall_dict = super(crm_phonecall, self).schedule_another_phonecall(
            cr, uid, ids, schedule_time, call_summary, user_id, section_id, categ_id, action, context)

        for call in self.browse(cr, uid, ids, context=context):
            if call.opportunity_id:
                self.write(cr, uid, phonecall_dict[call.id], {'opportunity_id': call.opportunity_id.id})

        return phonecall_dict
