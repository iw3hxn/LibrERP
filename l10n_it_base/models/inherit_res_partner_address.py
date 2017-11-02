# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2013 OpenERP Italian Community (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp.osv import orm, fields
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class res_partner_address(orm.Model):
    _inherit = 'res.partner.address'

    def _check_unique_default_type(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        for address in self.browse(cr, uid, ids, context):
            if address.partner_id and address.type in ('default', 'invoice'):
                address_ids = self.search(cr, uid, [('type', '=', address.type),
                                                    ('partner_id', '=', address.partner_id.id),
                                                    ], context=context)
                if len(address_ids) > 1:
                    _logger.debug(
                        u'####### Multiple {} Address ########'.format(address.type.capitalize()))
                    return False
                elif len(address_ids) < 1:
                    _logger.debug(
                        u'####### Ubnormal situation: partner with id "{0}" not found ########'.format(
                            address.partner_id.id))
                    return False
        return True

    def check_category(self, cr, uid, ids, field_names, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        country_obj = self.pool['res.country']

        for address in self.browse(cr, uid, ids, context):
            country_ids = country_obj.search(
                cr, uid, [('name', '=', address.country_id.name)], context=context)
            if country_ids:
                countries = country_obj.browse(cr, uid, country_ids, context)
                for country in countries:
                    for field_name in field_names:
                        if address.id not in result:
                            result[address.id] = {}

                        if getattr(country, field_name):
                            result[address.id][field_name] = False
                        elif not result[address.id].get(field_name, False):
                            result[address.id][field_name] = True
            else:
                for field_name in field_names:
                    if address.id not in result:
                        result[address.id] = {}
                    result[address.id][field_name] = False
        return result

    _columns = {
        'province': fields.many2one('res.province', string='Province', ondelete='restrict'),
        'region': fields.many2one('res.region', string='Region', ondelete='restrict'),
        'find_city': fields.boolean('Find City'),
        'enable_province': fields.function(
            check_category, string='Provincia?', type='boolean', readonly=True, method=True, multi=True),
        'enable_region': fields.function(
            check_category, string='Regione?', type='boolean', readonly=True, method=True, multi=True),
        'enable_state': fields.function(
            check_category, string='Stato?', type='boolean', readonly=True, method=True, multi=True, default=True),
        'cf_others': fields.char('C.F. aggiuntivi', size=128),
        'name_others': fields.char('Cointestatari', size=256),
    }

    _defaults = {
        'type': 'default',
    }

    _constraints = [
        (_check_unique_default_type, _('\n There is already an address of type default'), ['type', 'partner_id']),
    ]

    def on_change_zip(self, cr, uid, ids, zip_code=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {'value': {}}
        if zip_code and len(zip_code) > 3:
            city_obj = self.pool['res.city']
            city_ids = city_obj.search(cr, uid, [('zip', '=ilike', zip_code)], context=context)
            if not city_ids:
                city_ids = city_obj.search(cr, uid, [('zip', '=ilike', zip_code[:3] + 'xx')], context=context)

            if len(city_ids) == 1:
                city_obj = self.pool['res.city'].browse(cr, uid, city_ids[0], context)
                res = {'value': {
                    'zip': zip_code,
                    'province': city_obj.province_id and city_obj.province_id.id or False,
                    'region': city_obj.region and city_obj.region.id or False,
                    'country_id': city_obj.region.country_id and city_obj.region.country_id.id or False,
                    'city': city_obj.name,
                    'find_city': True,
                }}
        return res

    def on_change_city(self, cr, uid, ids, city, zip_code=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {'value': {'find_city': False}}
        if city:
            city_obj = self.pool['res.city']
            city_ids = city_obj.search(cr, uid, [('name', '=ilike', city.title())], context=context)
            if city_ids:
                city_row = city_obj.browse(cr, uid, city_ids[0], context)
                if zip_code:
                    zip_code = zip_code
                else:
                    zip_code = city_row.zip

                res = {'value': {
                    'province': city_row.province_id and city_row.province_id.id or False,
                    'region': city_row.region and city_row.region.id or False,
                    'zip': zip_code,

                    'country_id': city_row.region and
                                  city_row.region.country_id and
                                  city_row.region.country_id.id
                                  or False,

                    'city': city.title(),
                    'find_city': True,
                }}
        return res

    def on_change_province(self, cr, uid, ids, province, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {'value': {}}
        if province:
            province = self.pool['res.province'].browse(cr, uid, province, context)
            res = {'value': {
                'province': province.id,
                'region': province.region and province.region.id or False,
                'country_id': province.region and province.region.country_id and province.region.country_id.id or False
            }}
        return res

    def on_change_region(self, cr, uid, ids, region, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {'value': {}}
        if region:
            region_obj = self.pool['res.region'].browse(cr, uid, region, context)
            res = {'value': {
                'region': region,
                'country_id': region_obj.country_id and region_obj.country_id.id or False
            }}
        return res

    def _set_vals_city_data(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if 'city' in vals and 'province' not in vals and 'region' not in vals:
            if vals['city']:
                city_obj = self.pool['res.city']
                city_ids = city_obj.search(cr, uid, [('name', '=ilike', vals['city'].title())], context=context)
                if city_ids:
                    city = city_obj.browse(cr, uid, city_ids[0], context)
                    if 'zip' not in vals:
                        vals['zip'] = city.zip
                    if city.province_id:
                        vals['province'] = city.province_id.id
                    if city.region:
                        vals['region'] = city.region.id
                        if city.region.country_id:
                            vals['country_id'] = city.region.country_id.id
        return vals

    # Is correct move to l10n_it_account, there are an error because is call from crm_lead
    # def create(self, cr, uid, vals, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     vals = self._set_vals_city_data(cr, uid, vals, context)
    #     return super(res_partner_address, self).create(cr, uid, vals, context)
    #
    # def write(self, cr, uid, ids, vals, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     vals = self._set_vals_city_data(cr, uid, vals, context)
    #     return super(res_partner_address, self).write(cr, uid, ids, vals, context)
