# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Avanzosc <http://www.avanzosc.com>
#    Copyright (c) 2013 Andrei Levin (andrei.levin at didotech.com)
#
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
{
    "name": "Stock Move Extended",
    "version": "3.7.7.15",
    "depends": ["stock"],
    "author": "Didotech SRL",
    "category": "Custom Modules",
    "description": """
        Custom Modules. This module displays the unit price on the input stock move line, and also +/- based on direction
        Create new menu under "Products Move"

    """,
    'depends': ['stock'],
    'data': [
            'security/security.xml',
            'views/stock_move_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
