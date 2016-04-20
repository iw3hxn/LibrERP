# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    "name" : "Invoice Reopen",
    "version" : "1.1",
    "author" : "Camptocamp SA",
    "category": 'Accounting & Finance',
    'complexity': "normal",
    "description": """
Allows reopeing of unpaid invoices.
=====================================

This module allows to reopen (set to draft) unpaid invoices.
To comply with good accounting practice the existing posted move associated
with the invoice will be renamed (add [YYMMDD HHMISS]) and a new move (same name ending with *)
will be created with reversed debit/credit.
The renamed and new lines are reconciled.
If the invoice is printed AND stored as attachment the attachment will be renamed too.
This allows to change all content of the invoice if necessary.

    """,
    'website': 'http://www.camptocamp.com',
    "depends" : ["account"],
    'init_xml': [],
    'update_xml': ['account_reopen_view.xml','account_invoice_workflow.xml' ],
    'demo_xml': [],
    'installable': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
