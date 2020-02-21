# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>).
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
    "name": "Sales order Calendar ",
    "description": """
            I can see on sale order date for recall customer
        """,
    "version": "3.1.2.2",
    "author": "Didotech SRL",
    "website": "http://www.didotech.srl",
    "category": "Sales",
    "depends": [
        'sale',
        'sale_order_confirm',
        'sale_order_version',
    ],
    "init": [],
    "demo": [],
    "data": [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/crm_activity.xml',
    ],
    "installable": True,
    'active': True
}
