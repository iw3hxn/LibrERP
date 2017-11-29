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

{
    "name": "Product Extended",
    "version": "3.8.10.9",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    'category': 'Sales Management',
    "description": """
       Module extends functionality of the product module.
   
       Now on category there are a flag for show if exist same product or not. If no product is possible to unlink
       
       Module improves search, so product is searchable by more than one word written in any order.

       'inside script directory there are a script for update al database
    """,
    "depends": [
        'base',
        'product',
        'product_bom',
        'purchase',
        'sale'
    ],
    "data": [
        'views/product_view.xml',
        'views/product_supplierinfo_view.xml',
        'views/product_category_view.xml',
    ],
    "active": False,
    "installable": True,
    'auto_install': True
}
