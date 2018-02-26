# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product serial module for OpenERP
#    Copyright (C) 2008 Raphaël Valyi
#    2013-2014 Didotech SRL
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

LOT_SPLIT_TYPE_SELECTION = [
    ('none', 'None'),
    ('single', 'Single'),
    ('lu', 'Logistical Unit')
]


class product_product(orm.Model):
    _inherit = "product.product"

    _columns = {
        'lot_split_type': fields.selection(LOT_SPLIT_TYPE_SELECTION, 'Lot split type', required=True, help="None: no split ; single: 1 line/product unit ; Logistical Unit: split using the 1st Logistical Unit quantity of the product form packaging tab (to be improved to take into account all LU)"),
        'supplier_code': fields.related('seller_ids', 'product_code', type='char', string="Supplier Code"),
    }
    _defaults = {
        'lot_split_type': lambda *a: 'none',
    }


class product_ul(orm.Model):
    _inherit = "product.ul"
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
    }
