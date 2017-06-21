# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import datetime

from openerp import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class stock_location(orm.Model):
    _inherit = "stock.location"

    _columns = {
        'update_product_bylocation': fields.boolean('Show Product location quantity on db', help='If check create a columns on product_product table for get product for this location'),
        'product_related_columns': fields.char('Columns Name on product_product')
    }

    def update_product_by_location(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        location_ids = self.search(cr, uid, [('update_product_bylocation', '=', True)], context=context)
        location_vals = {}
        start_time = datetime.now()
        date_product_by_location_update = start_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if location_ids:
            product_obj = self.pool['product.product']
            for location in self.browse(cr, uid, location_ids, context):
                location_vals[location.id] = location.product_related_columns
            product_ids = product_obj.search(cr, uid, [('type', '!=', 'service')], context=context)
            product_context = context.copy()

            product_vals = {}
            for product_id in product_ids:
                product_vals[product_id] = {}

            for location_keys in location_vals.keys():
                product_context['location'] = location_keys
                for product in product_obj.browse(cr, uid, product_ids, product_context):
                    if location_vals[location_keys] and (product[location_vals[location_keys]] != product.qty_available):
                        product_vals[product.id][location_vals[location_keys]] = product.qty_available

            if product_vals:
                for product_id in product_vals.keys():
                    product_val = product_vals[product_id]
                    if product_val:
                        product_val['date_product_by_location_update'] = date_product_by_location_update
                        product_obj.write(cr, uid, product_id, product_val, context)

        end_time = datetime.now()
        duration_seconds = (end_time - start_time)
        duration = '{sec}'.format(sec=duration_seconds)
        _logger.info(u'update_product_by_location get in {duration}'.format(duration=duration))
        return True

    def create_product_by_location(self, cr, location_name, context):
        model_id = self.pool['ir.model.data'].get_object_reference(cr, SUPERUSER_ID, 'product', 'model_product_product')[1]
        fields_value = {
            'field_description': location_name,
            'groups': [[6, False, []]],
            'model_id': model_id,
            'name': 'x_{location_name}'.format(location_name=location_name).lower().replace(' ', '_'),
            'readonly': False,
            'required': False,
            'select_level': '0',
            'serialization_field_id': False,
            'translate': False,
            'ttype': 'float',
        }
        context_field = context.copy()
        context_field.update(
            {
                'department_id': False,
                'lang': 'it_IT',
                'manual': True,  # required for create columns on table
                'uid': 1
            }
        )

        fields_id = self.pool['ir.model.fields'].create(cr, SUPERUSER_ID, fields_value, context_field)
        return fields_id,  fields_value['name']

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if vals.get('update_product_bylocation', False):
            for location in self.browse(cr, uid, ids, context):
                field_id, field_name = self.create_product_by_location(cr, location.name, context)
                vals['product_related_columns'] = field_name
        return super(stock_location, self).write(cr, uid, ids, vals, context)
