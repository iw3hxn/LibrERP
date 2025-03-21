# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014-2016 Didotech srl (<http://www.didotech.com>).
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
    "name": "Purchase Order Extended",
    "version": "3.7.26.10",
    "author": "Didotech SRL",
    "website": "https://www.didotech.com",
    "category": 'Purchase',
    "description": """
        Module adds extra functionality to purchase_order:
            - on purchase order line add the sequence number
            - auto change of
    """,
    "depends": [
        'purchase',
        'core_extended',
        'stock_picking_extended',
        'base_address_contacts',
    ],
    "init_xml": [],
    "data": [
        'view/partner_view.xml',
        'view/purchase_order_view.xml',
        'view/purchase_order_menu.xml',
        'view/stock_move_view.xml'
    ],
    "active": False,
    "installable": True,
    'auto_install': True,
}
