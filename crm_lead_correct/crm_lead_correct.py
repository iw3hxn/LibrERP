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
from tools.translate import _
from openerp import SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


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

    def stage_next(self, cr, uid, ids, context=None):
        """This function computes next stage for case from its current stage
        using available stage for that case type
        """
        for crm in self.browse(cr, uid, ids, context=context):
            if crm.shop_id:
                if crm.sale_order and crm.shop_id.crm_sale_stage_ids:
                    raise orm.except_orm('Errore!', _("Can't change stage because is connect to a Sale Order"))
                    return False
        return self.stage_change(cr, uid, ids, '>', 'sequence', context)

    def stage_previous(self, cr, uid, ids, context=None):
        """This function computes previous stage for case from its current
        stage using available stage for that case type
        """
        for crm in self.browse(cr, uid, ids, context=context):
            if crm.shop_id:
                if crm.sale_order and crm.shop_id.crm_sale_stage_ids:
                    raise orm.except_orm('Errore!', _("Can't change stage because is connect to a Sale Order"))
                    return False
        return self.stage_change(cr, uid, ids, '<', 'sequence desc', context)

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        leads = self.browse(cr, uid, ids, context)
        for lead in leads:
            if lead.categ_id:
                value[lead.id] = lead.categ_id.color
            else:
                value[lead.id] = 'black'

        return value
   
    def _get_sale_order(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        # crm_lead_obj = self.pool['crm.lead']
        sale_order_obj = self.pool['sale.order']

        for crm_lead in self.browse(cr, uid, ids, context):
            partner_id = crm_lead.partner_id.id
            partner_address_id = crm_lead.partner_address_id.id
            if partner_address_id:
                result[crm_lead.id] = sale_order_obj.search(cr, uid, [('partner_id', '=', partner_id), ('partner_order_id', '=', partner_address_id)], context=context)
            else:
                result[crm_lead.id] = sale_order_obj.search(cr, uid, [('partner_id', '=', partner_id)], context=context)

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

    def _get_meeting_history(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        meeting_history = []
        for crm_lead in self.browse(cr, uid, ids, context):
            result[crm_lead.id] = {
                'meeting_smart_history': '',
                'last_meeting_date': False,
            }
            meeting_date = False
            for meeting in crm_lead.meeting_ids:
                meeting_date = datetime.strptime(meeting.date, DEFAULT_SERVER_DATETIME_FORMAT).date()
                meeting_history.append(meeting_date.strftime(DEFAULT_SERVER_DATE_FORMAT) or '')
                meeting_history.append(meeting.description or '')
                # todo write better function
                last_meeting_date = datetime.strptime(crm_lead.meeting_ids[0].date, DEFAULT_SERVER_DATETIME_FORMAT).date()

            if meeting_history:
                result[crm_lead.id]['meeting_smart_history'] = '\n'.join(meeting_history)
            if meeting_date:
                result[crm_lead.id]['last_meeting_date'] = last_meeting_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        return result

    def vat_change(self, cr, uid, ids, vat, context=None):

        if not vat:
            return False

        vat_country, vat_number = self.pool['res.partner']._split_vat(vat)
        if ids or not self.pool['res.partner'].simple_vat_check(cr, uid, vat_country, vat_number, context):
            return False

        vat = (vat_country + vat_number).upper()
        partner_vat = self.pool['res.partner'].search(cr, uid, [('vat', '=', vat)], context=context)
        if partner_vat:
            partner = self.pool['res.partner'].browse(cr, uid, partner_vat, context)[0]
            return {
                'value': {
                    'partner_name': partner.name,
                    'vat': partner.vat,
                    'partner_id': partner.id,
                    'street': partner.address and partner.address[0].street or '',
                    'zip': partner.address and partner.address[0].zip or '',
                    'city': partner.address and partner.address[0].city or '',
                    'province': partner.address and partner.address[0].province and partner.address[0].province.id or '',
                    'region': partner.address and partner.address[0].region and partner.address[0].region.id or '',
                    'country_id': partner.address and partner.address[0].country_id and partner.address[0].country_id.id or '',
                }
            }
        else:
            partner_vat_all = self.pool['res.partner'].search(cr, SUPERUSER_ID, [('vat', '=', vat)], context=context)
            if partner_vat_all:
                partner = self.pool['res.partner'].browse(cr, uid, partner_vat_all, context)[0]
                raise orm.except_orm('Errore!',
                    "Cliente {partner} con P.Iva {vat} già presente ed assegnato all'utente {user}!".format(vat=vat, partner=partner.name, user=partner.user_id.name or ''))
                return False
            else:
                vat_change = self.pool['res.partner'].vat_change(cr, uid, ids, vat, context)
                vat_value = vat_change.get('value', False)
                if vat_value:
                    address = vat_value.get('address', False) and vat_value['address'][0][2] or {}
                    return {
                        'value': {
                            'partner_name': vat_value.get('name', ''),
                            'vat': vat,
                            'street': address.get('street', ''),
                            'zip': address.get('zip', ''),
                            'city': address.get('city', ''),
                            'province': address.get('province', False),
                            'region': address.get('region', False),
                            'country_id': address.get('country_id', False),
                        }
                    }

        return {'value': {}}

    def action_view_sale_order(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''

        mod_obj = self.pool['ir.model.data']
        act_obj = self.pool['ir.actions.act_window']

        result = mod_obj.get_object_reference(cr, uid, 'sale', 'action_order_form')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        # compute the number of delivery orders to display
        sale_ids = []

        for crm in self.browse(cr, uid, ids, context=context):
            sale_ids += [crm.sale_order.id]

        # choose the view_mode accordingly
        if len(sale_ids) > 1:
            result['domain'] = "[('id','in'," + str(tuple(sale_ids)) + ")]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'sale', 'view_order_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = sale_ids and sale_ids[0] or False
        result['context'] = {'nodelete': '1', 'nocreate': '1'}

        return result

    _columns = {
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Dal"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Al"),
        'partner_address_id': fields.many2one('res.partner.address', 'Partner Contact'),
        'province': fields.many2one('res.province', string='Province', ondelete='restrict'),
        'region': fields.many2one('res.region', string='Region', ondelete='restrict'),
        'find_city': fields.boolean('Find City'),
        'website': fields.char('Website', size=64, help="Website of Partner."),
        'function_id': fields.many2one('res.contact.function', 'Function'),
        'phonecall_ids': fields.one2many('crm.phonecall', 'opportunity_id', 'Phonecalls'),
        'meeting_ids': fields.one2many('crm.meeting', 'opportunity_id', 'Meetings'),
        'contact_id': fields.many2one('res.partner.address.contact', 'Contact'), 
        'partner_category_id': fields.many2one('res.partner.category', 'Partner Category'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True),
        'sale_order_ids': fields.function(_get_sale_order, 'Sale Order', type='one2many', relation="sale.order", readonly=True, method=True),
        'crm_lead_ids': fields.function(_get_crm_lead, 'Opportunity', type='one2many', relation="crm.lead", readonly=True, method=True),
        'vat': fields.char('VAT', size=64),
        'sale_order': fields.many2one('sale.order', string='Created Sale Order'),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'meeting_smart_history': fields.function(_get_meeting_history, string='Meeting', type='text', readonly=True, multi='sums'),
        'last_meeting_date': fields.function(_get_meeting_history, string='Last Meeting Date', type='date', readonly=True, multi='sums', store=True),
    }

    _defaults = {
        'name': '/',
    }

    _order = "create_date desc"

    def _lead_create_partner(self, cr, uid, lead, context=None):
        # todo check on company if required vat on partner creation from lead
        partner_obj = self.pool['res.partner']

        if partner_obj._columns.get('vat') and partner_obj._columns['vat'].required and not lead.vat:
            raise orm.except_orm(_('Error :'), _("VAT Required"))
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
            'category_id': lead.partner_category_id and [(6, 0, [lead.partner_category_id.id])],
            'vat': lead.vat,
        }, context=context)

        return partner_id

    def _lead_create_partner_address(self, cr, uid, lead, partner_id, context=None):
        address_obj = self.pool['res.partner.address']
        address_ids = address_obj.search(cr, uid, [('partner_id', '=', partner_id), ('type', '=', 'default')])
        if address_ids:
            address_id = address_ids[0]
        else:
            address_id = address_obj.create(cr, uid, {
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

    def onchange_partner_id(self, cr, uid, ids, part, email=False, context=None):
        res = super(crm_lead_correct, self).onchange_partner_id(cr, uid, ids, part, email, context)
        domain = {'contact_id': []}
        if part:
            domain = {'contact_id': [('partner_id', '=', part)]}
        res['domain'] = domain
        print domain
        return res

    def onchange_contact_id(self, cr, uid, ids, contact_id):
        """This function returns value of partner email based on Partner Address
        :param ids: List of case IDs
        :param add: Id of Partner's address
        :param email: Partner's email ID
        """
        data = {'value': {'email_from': False, 'phone': False}}
        context = self.pool['res.users'].context_get(cr, uid)

        if contact_id:
            contact = self.pool['res.partner.address.contact'].browse(cr, uid, contact_id, context)
            data['value'] = {
                'email_from': contact and contact.email or False,
                'phone': contact and contact.mobile or False,
                'partner_address_id': contact.address_id and contact.address_id.id or False,
                'partner_id': contact.address_id and contact.address_id.partner_id and contact.address_id and contact.address_id.partner_id.id or False,
            }
        return data

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
        context = self.pool['res.users'].context_get(cr, uid)

        for lead in self.browse(cr, uid, ids, context):
            partner_vals = {}
            if lead.partner_id:
                if not lead.partner_id.email and vals.get('email_from', False):
                    partner_vals['email'] = vals['email_from']

                if not lead.partner_id.phone and not lead.partner_id.mobile and vals.get('phone', False):
                    partner_vals['phone'] = vals['phone']

                if partner_vals:
                    address_ids = address_obj.search(cr, uid, [
                        ('partner_id', '=', lead.partner_id.id), ('type', '=', 'default')], context=context)
                    if address_ids:
                        address_obj.write(cr, uid, address_ids[0], partner_vals, context)
                    else:
                        partner_vals['type'] = 'default'
                        partner_vals['partner_id'] = lead.partner_id.id
                        address_obj.create(cr, uid, partner_vals, context)
        return True

    def create(self, cr, uid, vals, context=None):
        vals = self.pool['res.partner.address']._set_vals_city_data(cr, uid, vals)

        if vals.get('name', '/') == '/':
            sequence_data_id = self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'crm_lead_correct', 'seq_lead_item')
            if sequence_data_id:
                new_name = self.pool['ir.sequence'].next_by_id(cr, uid, sequence_data_id[1], context=context)
                vals.update({'name': new_name})
        if vals.get('vat', False):
            vals['vat'] = vals['vat'].upper()

        result = super(crm_lead_correct, self).create(cr, uid, vals, context=context)

        if vals.get('email_from', False) or vals.get('phone', False):
            self.check_address(cr, uid, [result], vals)

        return result

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {'force_stage_id': True}

        vals = self.pool['res.partner.address']._set_vals_city_data(cr, uid, vals)

        if vals.get('stage_id', False) and not context.get('force_stage_id', False):
            for crm in self.browse(cr, uid, ids, context=context):
                if crm.shop_id:
                    if crm.sale_order and crm.shop_id.crm_sale_stage_ids:
                        raise orm.except_orm('Errore!', _("Can't change stage because is connect to a Sale Order"))
                        return False

        result = super(crm_lead_correct, self).write(cr, uid, ids, vals, context=context)

        if vals.get('email_from', False) or vals.get('phone', False):
            self.check_address(cr, uid, ids, vals)
        if vals.get('vat', False):
            vals['vat'] = vals['vat'].upper()

        return result

    def copy(self, cr, uid, ids, default, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({'name': '/', 'sale_order': False})
        return super(crm_lead_correct, self).copy(cr, uid, ids, default, context)


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
