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

from datetime import datetime

from mail.mail_message import to_email
from openerp import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from tools.translate import _

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


class CrmLead(orm.Model):
    _inherit = 'crm.lead'

    _index_name = 'crm_lead_partner_address_id_index'

    def _auto_init(self, cr, context={}):
        res = super(CrmLead, self)._auto_init(cr, context)
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s', (self._index_name,))
        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON crm_lead (partner_address_id)'.format(name=self._index_name))
        return res

    def stage_next(self, cr, uid, ids, context=None):
        """This function computes next stage for case from its current stage
        using available stage for that case type
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        for crm in self.browse(cr, uid, ids, context=context):
            if crm.shop_id:
                if crm.sale_order_id and crm.shop_id.crm_sale_stage_ids:
                    raise orm.except_orm('Errore!', _("Can't change stage because is connect to a Sale Order"))
        return self.stage_change(cr, uid, ids, '>', 'sequence', context)

    def stage_previous(self, cr, uid, ids, context=None):
        """This function computes previous stage for case from its current
        stage using available stage for that case type
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        for crm in self.browse(cr, uid, ids, context=context):
            if crm.shop_id:
                if crm.sale_order_id and crm.shop_id.crm_sale_stage_ids:
                    raise orm.except_orm('Errore!', _("Can't change stage because is connect to a Sale Order"))
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
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        # crm_lead_obj = self.pool['crm.lead']
        sale_order_obj = self.pool['sale.order']

        for lead in self.browse(cr, uid, ids, context):
            partner_id = lead.partner_id.id
            partner_address_id = lead.partner_address_id.id
            if partner_address_id:
                result[lead.id] = sale_order_obj.search(cr, uid, [('partner_id', '=', partner_id), ('partner_order_id', '=', partner_address_id)], context=context)
            else:
                result[lead.id] = sale_order_obj.search(cr, uid, [('partner_id', '=', partner_id)], context=context)

        return result

    def _get_visible_sale_order_id(self,cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        # crm_lead_obj = self.pool['crm.lead']
        sale_order_obj = self.pool['sale.order']

        for lead in self.browse(cr, uid, ids, context):
            res = False
            if lead.partner_id:
                so_number = sale_order_obj.search(cr, uid, [('partner_id', '=', lead.partner_id.id)], context=context, count=True)
                if so_number:
                    res = True
            result[lead.id] = res
        return result

    def _get_crm_lead(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        crm_lead_obj = self.pool['crm.lead']
        for crm in crm_lead_obj.read(cr, uid, ids, ['partner_id', 'partner_address_id'], context, load='_obj'):
            # name = crm['name']
            partner_id = crm['partner_id']
            if not partner_id:
                result[crm['id']] = []
                continue
            contact_id = crm['partner_address_id']
            domain = [('partner_id', '=', partner_id)]
            if contact_id:
                domain.append(('partner_address_id', '=', contact_id))

            result[crm['id']] = crm_lead_obj.search(cr, uid, domain, context=context)
        return result

    def _get_meeting_history(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        meeting_history = []
        for crm in self.browse(cr, uid, ids, context):
            result[crm.id] = {
                'meeting_smart_history': '',
                'last_meeting_date': False,
            }
            meeting_date = False
            for meeting in crm.meeting_ids:
                meeting_date = datetime.strptime(meeting.date, DEFAULT_SERVER_DATETIME_FORMAT).date()
                meeting_history.append(meeting_date.strftime(DEFAULT_SERVER_DATE_FORMAT) or '')
                meeting_history.append(meeting.description or '')
                # todo write better function
                last_meeting_date = datetime.strptime(crm.meeting_ids[0].date, DEFAULT_SERVER_DATETIME_FORMAT).date()

            if meeting_history:
                result[crm.id]['meeting_smart_history'] = '\n'.join(meeting_history)
            if meeting_date:
                result[crm.id]['last_meeting_date'] = last_meeting_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        return result

    def vat_change(self, cr, uid, ids, vat, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

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
                raise orm.except_orm(u'Errore!',
                    u"Cliente {partner} con P.Iva {vat} già presente ed assegnato all'utente {user}!".format(vat=vat, partner=partner.name, user=partner.user_id.name or ''))
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
        sale_order_obj = self.pool['sale.order']

        result = mod_obj.get_object_reference(cr, uid, 'sale', 'action_order_form')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        # compute the number of delivery orders to display
        sale_ids = []

        for crm in self.browse(cr, uid, ids, context=context):
            sale_ids += [crm.sale_order_id.id]

        if sale_order_obj._columns.get('sale_version_id', False):
            original_sale_ids = sale_ids
            for order in sale_order_obj.read(cr, uid, sale_ids, ['sale_version_id'], load='_obj'):
                if order['sale_version_id']:
                    original_sale_ids.append(order['sale_version_id'])
            original_sale_ids = list(set(original_sale_ids))
            if original_sale_ids:
                search_domain = ['|', ('sale_version_id', 'in', original_sale_ids), ('id', 'in', sale_ids)]
            else:
                search_domain = [('id', 'in', sale_ids)]
            sale_ids = sale_order_obj.search(cr, uid, search_domain, context=context)

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
        'visible_sale_order_id': fields.function(_get_visible_sale_order_id, type='boolean'),
        'sale_order_id': fields.many2one('sale.order', string='Created Sale Order', oldname='sale_order', index=True),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'meeting_smart_history': fields.function(_get_meeting_history, string='Meeting', type='text', readonly=True, multi='sums'),
        'last_meeting_date': fields.function(_get_meeting_history, string='Last Meeting Date', type='date', readonly=True, multi='sums', store=True),
    }

    _defaults = {
        'name': '/',
    }

    _order = "create_date desc"

    def _lead_create_partner(self, cr, uid, lead, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
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
        context = context or self.pool['res.users'].context_get(cr, uid)
        address_obj = self.pool['res.partner.address']
        address_ids = address_obj.search(cr, uid, [('partner_id', '=', partner_id), ('type', '=', 'default')], context=context)
        if address_ids:
            address_id = address_ids[0]
        else:
            address_id = address_obj.create(cr, uid, {
                'type': 'default',
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
            }, context)

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
            contact_id = contact_partner_address_obj.create(cr, uid, vals, context)
            lead.write({'contact_id': contact_id})
        return address_id

    def onchange_partner_id(self, cr, uid, ids, part, email=False, context=None):
        res = super(CrmLead, self).onchange_partner_id(cr, uid, ids, part, email, context)
        domain = {'contact_id': []}
        if part:
            domain = {'contact_id': [('partner_id', '=', part)]}
        res['domain'] = domain
        return res

    def onchange_partner_address_id(self, cr, uid, ids, partner_address_id, email_from):
        res = super(CrmLead, self).onchange_partner_address_id(cr, uid, ids, partner_address_id, email_from)
        if partner_address_id:
            partner_address = self.pool['res.partner.address'].browse(cr, uid, partner_address_id)
            find_city = False
            if partner_address.zip:
                find_city = True
                res['value'].update(zip=partner_address.zip)
            if partner_address.province:
                find_city = True
                res['value'].update(province=partner_address.province.id)
            if partner_address.region:
                find_city = True
                res['value'].update(region=partner_address.region.id)
            if find_city:
                res['value'].update(find_city=find_city)
        return res

    def onchange_sale_order_id(self, cr, uid, ids, sale_order_id, context=None):
        ref = False
        if sale_order_id:
            ref = 'sale.order,{}'.format(sale_order_id)
        res = {
            'value': {
                'ref': ref
            },
        }
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

    def check_address(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        address_obj = self.pool['res.partner.address']
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
        context = context or self.pool['res.users'].context_get(cr, uid)

        vals = self.pool['res.partner.address']._set_vals_city_data(cr, uid, vals)

        if vals.get('name', '/') == '/':
            sequence_data_id = self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'crm_lead_correct', 'seq_lead_item')
            if sequence_data_id:
                new_name = self.pool['ir.sequence'].next_by_id(cr, uid, sequence_data_id[1], context=context)
                vals.update({'name': new_name})
        if vals.get('vat', False):
            vals['vat'] = vals['vat'].upper()

        result = super(CrmLead, self).create(cr, uid, vals, context=context)

        if vals.get('email_from', False) or vals.get('phone', False):
            self.check_address(cr, uid, [result], vals, context)

        return result

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context.update({'force_stage_id': True})
        if isinstance(ids, (int, long)):
            ids = [ids]

        vals = self.pool['res.partner.address']._set_vals_city_data(cr, uid, vals)

        if vals.get('stage_id', False) and not context.get('force_stage_id', False):
            for crm in self.browse(cr, uid, ids, context=context):
                if crm.shop_id:
                    if crm.sale_order_id and crm.shop_id.crm_sale_stage_ids:
                        raise orm.except_orm('Errore!', _("Can't change stage because is connect to a Sale Order"))

        result = super(CrmLead, self).write(cr, uid, ids, vals, context=context)

        if vals.get('email_from', False) or vals.get('phone', False):
            self.check_address(cr, uid, ids, vals, context)
        if vals.get('vat', False):
            vals['vat'] = vals['vat'].upper()

        return result

    def copy(self, cr, uid, ids, default, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if default is None:
            default = {}
        default.update({'name': '/', 'sale_order_id': False})
        return super(CrmLead, self).copy(cr, uid, ids, default, context)


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
