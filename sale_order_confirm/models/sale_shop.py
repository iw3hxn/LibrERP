# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-2015 Didotech srl (<http://www.didotech.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
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

from openerp.osv import orm, fields
import decimal_precision as dp


class sale_shop(orm.Model):
    _inherit = 'sale.shop'

    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'sale_order_have_minimum': fields.boolean('Minimum Amount', help='The Sale Order of this shop have a Minimun Amount'),
        'sale_order_minimun': fields.float('Minimum Amount of Sale Order', digits_compute=dp.get_precision('Sale Price')),
        'user_allow_minimun_id': fields.many2one('res.users', 'User that can validate'),
        'product_allow_minimun_id': fields.many2one('product.product', string='Product that can validate', domain=[('type', '=', 'service')]),
        'user_tech_validation_id': fields.many2one('res.users', 'User that can be Tech Validation'),
        'user_manager_validation_id': fields.many2one('res.users', 'User that can be Manager Validation'),
        'user_supervisor_validation_id': fields.many2one('res.users', 'User that can be Verification after Customer Confirmation', oldname='user_supervisor_validation'),
    }

    _order = 'sequence, name'

    _defaults = {
        'sequence': 10
    }