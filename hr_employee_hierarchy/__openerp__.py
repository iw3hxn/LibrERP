# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2013 Didotech srl (<http://www.didotech.com>). All Rights Reserved
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
    "name": "Employee Hierarchy",
    "version": "1.0.0",
    "author": "Didotech srl",
    "website": "www.didotech.com",
    "category": "Generic Modules/Others",
    "description": """
This module introduce hierarchic relationship between Employees, so Manager acquire
rights that his Emplyees has. It also prevent Employee to take decisions for others
(For example create Meetings, Phonecalls or Tasks)
    """,
    "depends": [
        "base",
        'project',
        'crm',
        'hr'
    ],
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
    ],
    'images': [
    ],
    "active": False,
    "installable": True,
}
