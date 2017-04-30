# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2015 Didotech srl (<http://www.didotech.com>).
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
    "name": "HR Expense Extended",
    "version": "3.0.0.2",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": 'Human Resources',
    "description": """
        Module extends functionality of the hr_attendance:
           * on employee tree view show the state
           * opern employee on tree view 
    """,
    "depends": [
        'base',
        'hr_attendance',
    ],
    "data": [
        'views/hr_attendance_view.xml',
        'views/hr_employee_view.xml',
    ],
    "active": False,
    "installable": True,

}
