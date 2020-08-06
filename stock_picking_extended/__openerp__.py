# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014-2020 Didotech SRL (<http://didotech.com>).
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
    'name': 'Stock picking extended',
    'version': '3.47.58.63',
    'category': 'Others',
    'description': """LibrERP - Stock picking extension

Functionalities:
    - different shipping address for consignement order
    - correct wkfl in stock, sale, invoice
    - add user for stock_journal
""",

    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'stock', 
        'sale',
        'sale_journal',
        'account', 
        'delivery',
        'c2c_sequence_fy',     # ricomincia da 0 le sequenze ogni anno
        'sale_margin',
        'purchase',
        'core_extended',
        'res_users_helper_functions',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/journal_security.xml',
        'security/security.xml',
        'views/picking_view.xml',
        'views/carriage_condition_view.xml',
        'views/transportation_condition_view.xml',
        'views/goods_description_view.xml',
        'views/stock_picking_menu.xml',
        'views/stock_journal_view.xml',
        'views/stock_location_view.xml',
        'views/company_view.xml',
        'views/res_partner_view.xml',
        'views/res_partner_address_view.xml',
        'views/purchase_order_view.xml',
        'views/sale_order_view.xml',
        'views/stock_move_group_view.xml',
        'views/stock_inventory_view.xml',
        'wizard/print_stock_move_group_views.xml',
        'reports/stock_move_group_report.xml',
        'data/sale_data.xml',
        'data/stock.journal.csv',
        'data/crontab_data.xml'
    ],
    "demo": [],
    "test": [
    ],
    "active": False,
    "installable": True
}
