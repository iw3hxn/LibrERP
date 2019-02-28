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
    "name": "Purchase No Gap",
    "version": "3.2.3.3",
    "author": "Camptocamp Austria, Didotech srl",
    "category": 'Purchase Management',
    'complexity': "easy",
    "description": """
Purchase orders no gap and use of order date for sequence
=========================================================

    """,
    'website': 'http://www.didotech.com',
    "depends": ["purchase", "sale"],
    'data': [
        'views/purchase_view.xml',
        'views/sale_shop_view.xml',
        'data/purchase_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
