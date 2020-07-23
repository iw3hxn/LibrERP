# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014-2017 Didotech srl (<http://www.didotech.com>).
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
    "name": "Set Supplier inside Sale Order",
    "version": "3.7.27.14",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": 'Sale',
    "description": """
       Module gives possibility to select a supplier inside sale order line.
       When sale order is confirmed purchase order is created if procurement method is "to order".
       If no supplier is selected purchase requisition is created.
    """,
    "depends": [
        'base',
        'sale',
        'sale_order_confirm',
        'product_bom',
        'sale_bom',
        'dt_product_brand',
        'stock_picking_extended',
        'purchase_no_gap',
        'purchase_discount',
        'purchase_requisition_extended'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/inherit_sale_order.xml',
        'views/inherit_purchase_order.xml',
    ],
    "active": False,
    "installable": True,
}
