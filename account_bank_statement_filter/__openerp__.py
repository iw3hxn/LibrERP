# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>).
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
    "name": "Account Bank Statement Filter",
    "version": "3.2.4.5",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": 'Accounting & Finance',
    "description": """
        Module adds extra functionality to account bank statement:
            - possibility to filter statement by year
            - possibility to see statement of last or current month
            - possibility to see statement where there are a selected partner
    """,
    "depends": [
        'base',
        'account',
    ],
    "data": [
        'views/account_bank_view.xml',
        'views/account_bank_statement_line_view.xml'
    ],
    "active": False,
    "installable": True,
    'auto_install': True
}
