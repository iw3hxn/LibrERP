# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2015 Didotech SRL (info @ didotech.com).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
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


{
    'name': "HS Codes",
    'version': "3.0.0.1",
    'author': "Didotech SRL",
    'website': "www.didotech.com",
    'category': "Prduct",
    'depends': ['base', 'product', ],
    'init_xml': ['security/ir.model.access.csv'],
    'description': """Add HS CODE to product, includes HS codes based on data : http://tariffdata.wto.org/ReportersAndProducts.aspx
    Also script for
    """,
    'update_xml': [
        'hs_view.xml',
        'data/hs.category.csv',
        'data/hs.code.csv',
    ],
    'installable': True,
    'active': False,
}
