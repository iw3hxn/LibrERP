# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class product_template(orm.Model):
    _inherit = 'product.template'

    _columns = {
        'product_history': fields.one2many('product.price.history', 'product_id', 'Price History', readonly=True, ondelete='cascade'),
    }

    def write(self, cr, uid, ids, values, context=None):
        """
        Add old Sale Price or Sale Cost to historial
        """
        for prod_template in self.browse(cr, uid, ids, context=context):
            if ('list_price' in values and prod_template.list_price != values['list_price']) or \
               ('standard_price' in values and prod_template.standard_price != values['standard_price']):

                history_values = {
                    'user_id': uid,
                    'product_id': prod_template.id,
                    'date_to': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }
                if values.get('list_price', False):
                    history_values.update({
                        'list_price': prod_template.list_price,
                        'new_list_price': values['list_price'],
                    })
                if values.get('standard_price', False):
                    history_values.update({
                        'standard_price': prod_template.standard_price,
                        'new_standard_price': values['standard_price'],

                    })

                self.pool['product.price.history'].create(cr, uid, history_values, context=context)

        return super(product_template, self).write(cr, uid, ids, values, context=context)


class pricelist_partnerinfo(orm.Model):

    _inherit = 'pricelist.partnerinfo'

    def write(self, cr, uid, ids, values, context=None):
        """
        Add old Sale Price or Sale Cost to historial
        """
        for partner_info in self.browse(cr, uid, ids, context=context):
            if 'price' in values and partner_info.price != values['price']:
                product_id = partner_info.suppinfo_id.product_id.id
                supplier_id = partner_info.suppinfo_id.name.id
                history_values = {
                    'user_id': uid,
                    'product_id': product_id,
                    'date_to': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'supplier_id': supplier_id
                }

                if values.get('price', False):
                    history_values.update({
                        'standard_price': partner_info.price,
                        'new_standard_price': values['price'],

                    })
                self.pool['product.price.history'].create(cr, uid, history_values, context=context)

        return super(pricelist_partnerinfo, self).write(cr, uid, ids, values, context=context)


class product_product(orm.Model):
    _inherit = 'product.product'

    def copy(self, cr, uid, ids, default, context=None):
        if not default:
            default = {}
        default.update({
            'product_history': []
        })
        return super(product_product, self).copy(cr, uid, ids, default, context=context)
