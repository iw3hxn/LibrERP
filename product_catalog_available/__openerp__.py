# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Bortolatto Ivan. ( ivan.bortolatto(at)didotech.com )
#    Copyright (C) 2013 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
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
{
    'name': 'Product Catalog Report',
    'version': '6.1.2',
    'category': 'General',
    'description': """
        A report of product catalog to list the products with images and price appropriatly to the assinged pricelist.
        Difference with 'product_catalog_extend' module, is presence column 'Quantity Available'
        Version for Openerp 6.1
    """,
    "author": "Didotech",
    "website": "www.didotech.com",
    'depends': [
        'base', 'sale', 'product',
    ],
    'init_xml': [
        'wizard/product_catalog_available.xml',
    ],
    'update_xml': [
        'wizard/product_catalog_available.xml',
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
