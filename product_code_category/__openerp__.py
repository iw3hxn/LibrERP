# -*- coding: utf-8 -*-
##############################################################################
#
#    product_code_category module for OpenERP, Generate product code when product was created
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#    Copyright (C) 2013 Didotech SRL (<http://www.didotech.com/>)
#    This file is a part of product_code_category
#
#    product_code_category is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    product_code_category is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product Code Category',
    'version': '3.1.3.2',
    'category': 'Generic Modules/Products',
    'description': """This module automatically creates a product code, depending of the product's category, at the product's creation""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'base',
        'product'
    ],
    'init_xml': [
        'product_code_category_data.xml'
    ],
    'images': [
        'images/accueil.png',
        'images/syleam.png',
    ],
    'update_xml': [
        'product_code_category_view.xml'
    ],
    'demo_xml': [],
    'test': [
        'test/product_code_category.yml',
    ],
    #'external_dependancies': {'python': ['kombu'], 'bin': ['which']},
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
