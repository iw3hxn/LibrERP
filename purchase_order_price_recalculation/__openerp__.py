# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2016 Didotech SRL
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Sale Pricelist Update",
    "version": "3.0.0.0",
    "depends": ["sale"],
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": "Custom Modules",
    "description": """
    This module provide :
        * An update system for purchase order lines' unit price when the pricelist is changed.
    """,
    'data': [
        "views/purchase_order_view.xml"
    ],
    'installable': True,
    'active': False,
}