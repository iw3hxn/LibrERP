# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
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
    "name": "Account Invoice extended",
    "version": "3.3.11.11",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": "Generic Modules/Accounting",
    "description": """
        Module extendes and fixes Account Invoice functionality:
        Set nocreate also on account.move.line
        Fix: don't copy the owner of the invoice
        2 new groups for see the different:
            * Invoice Supplier
            * Invoice Customer

        No automatic email send

        Clear Account Move menu on Customer/Supplier Invoice

        Add adaptative function: the system learn.. form invoice to partner form

    """,
    "depends": [
        'base',
        'account',
        'web_hide_buttons',
        'account_due_list'
    ],
    "data": [
        'security/account_security.xml',
        'views/account_view.xml',
        'views/account_menu.xml',
        'views/account_workflow.xml',
        'views/account_move_journal_view.xml',
        'views/account_menu_clear.xml',
        'views/fiscal_position_view.xml',
        'workflows/account_invoice_workflow.xml',
    ],
    "active": False,
    "installable": True,

}
