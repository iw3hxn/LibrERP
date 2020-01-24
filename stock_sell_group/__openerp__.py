# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014-2019 Didotech SRL (<http://didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Stock Sell Group',
    'version': '3.1.0.0',
    'category': 'Others',
    'description': """LibrERP - Stock picking extension

Functionalities:
    - Show all the sell
""",

    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'stock',
        'core_extended',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/stock_sell_group_view.xml',
        'views/stock_sell_group_product_view.xml',
    ],
    "demo": [],
    "test": [
    ],
    "active": False,
    "installable": True
}
