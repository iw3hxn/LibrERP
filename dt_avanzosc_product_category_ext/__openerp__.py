
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#    
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Avanzosc Product Category Extension", 
    "version": "3.0.8.10",
    "depends": [
        "product",
        "product_bom",
        'product_no_tax'
    ],
    "author": "AvanzOSC, Didotech SRL",
    "category": "Custom Modules",
    "description": """
        Avanzosc Custom Modules. Defined in Categories the Provision type, Procure Method and the Supply method

    """,
    'data': [
        'views/product_category_ext_view.xml',
        'views/product_product_ext_view.xml',
        'views/company_view.xml'
    ],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
