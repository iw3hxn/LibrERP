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
    "name": "Picking Reopen",
    "version": "3.1.2.2",
    "author": "Camptocamp SA",
    "category": 'Warehouse Management',
    'complexity': "normal",
    "description": """
Allows reopening of uninvoiced and canceled pickings.
=====================================================

This module allows to reopen (set to Ready to Process) uninvoiced pickings
as long as no other stock moves for products with cost method "average price" 
of this picking are confirmed.
The intention is to allow to correct errors or add missing info which becomes 
usually only visible after printing the picking.

    """,
    'website': 'http://www.camptocamp.com',
    "depends" : [
        "stock",
        #"account_invoice_reopen"
    ],
    'init_xml': [],
    'update_xml': [
        'stock_view.xml',
        'stock_workflow.xml',
        'data/stock.journal.csv'
    ],
    'demo_xml': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
