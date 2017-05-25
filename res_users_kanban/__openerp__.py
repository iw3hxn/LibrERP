# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Didotech SRL
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Partner Directory",
    "version": "0.2.3.1",
    "author": "Didotech SRL",
    "category": "Partner",
    "sequence": 12,
    'complexity': "easy",
    "website": "http://www.didotech.com",
    'depends': ['web', 'base'],
    "description": """
Add kanban view on Users
    """,
    'data': ['views/res_users_view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    # "css": ['static/src/css/partner.css'],
}
