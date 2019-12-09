##############################################################################
#
#    Copyright (C) 2013-2018 Didotech srl (<http://www.didotech.com>).
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
    "name": "Bom in Sales Orders",
    "version": "3.5.21.23",
    "category": "Sales Management",
    "description": """
This module adds the 'BOM' on sales order.
==========================================

    """,
    "author": "Didotech Srl",
    "depends": [
        'sale',
        'mrp',
        'dt_product_serial'
    ],
    "demo_xml": [],
    "update_xml": [
        "security/ir.model.access.csv",
        "views/inherit_sale_order.xml"
    ],
    "auto_install": False,
    "installable": True,
}
