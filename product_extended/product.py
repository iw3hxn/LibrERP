# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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


class product_product(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'last_purchase_price': fields.float('Last purchase price', readonly=True),
        'last_purchase_date': fields.date('Last purchase date', readonly=True),
        'last_supplier_id': fields.many2one('res.partner', 'Last Supplier', readonly=True),
        'last_sale_price': fields.float('Last sale price', readonly=True),
        'last_sale_date': fields.date('Last sale date', readonly=True),
        'last_customer_id': fields.many2one('res.partner', 'Last Customer', readonly=True),
    }
