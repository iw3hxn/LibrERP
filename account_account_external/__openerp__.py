# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2023 All Rights Reserved
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
    "name": "Account Account Extended",
    "version": "6.1.0.0.0",
    "author": "Odoo SA",
    "website": "",
    "category": "Base",
    "description": """
        Module extended OpenERP core functionality
        
        Now is possible to add external code for chart of account

    """,
    "depends": [
        'account',
        'l10n_it_fatturapa_out'
    ],
    "data": [
        'views/account_account_view.xml',
        'views/account_bank_statement_view.xml',
        'data/ir_cron.xml'
    ],
    "active": False,
    "installable": True,
    "auto_install": True,
}
