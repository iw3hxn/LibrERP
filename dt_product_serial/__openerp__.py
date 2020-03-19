# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2008 Raphaël Valyi
#    Copyright (C) 2012-2014 Didotech srl
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
    "name": "Unique serial number management",
    "version": "3.8.25.23",
    "author": "Akretion, NaN·tic, Didotech SRL",
    "website": "http://www.akretion.com",
    "depends": [
        'stock'
    ],
    "category": "Generic Modules/Inventory Control",
    "license": "AGPL-3",
    "description": """Turns production lot tracking numbers into unique per product instance code (serial number).
    Moreover, it
    1) adds a new selection field on the product form to enable or disable this behavior and with split type choice (you should also enable in/out tracking)
    2) then forbids to perform a move if a move involves more than one product instance
    3) automagically splits up picking list movements into one movement per product instance or logistical unit packing qty (in that case, only the first LU is taken into account at the present time. Improvement to take them all to be done !!!)
    4) turns incoming pickings into an editable grid where you can directly type the codes
    of a new production and tracking number/code to create and associate to the move (it also checks it
    doesn't exist yet)
    5) decide if a move inside a picking is a balance of sale/purchase order
    6) manage pallet

    We would also like to extend this module to split automatic production orders (from MRP engine) into several individual production orders in order
    to make it easy to encode the serial numbers in the production. Let us know if you would like that simple extension to be made.
    """,
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/pallet_view.xml",
        "views/company_view.xml",
        "views/stock_view.xml",
        'views/partner_view.xml',
        # "wizard/stock_splitinto_view.xml",
        "wizard/stock_move_view.xml",
        "wizard/stock_partial_picking.xml",
    ],
    "active": False,
    "installable": True
}
