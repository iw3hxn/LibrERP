##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 Didotech srl (<http://www.didotech.com>).
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
    "name": "Show Bom in Product",
    "version": "2.0.3.1",
    "category": "Sales Management",
    "description": """
        This module adds the 'BOM' on Product. And also use BOM as WBS
        ==============================================================
        
    """,
    "author": "Didotech Srl",
    "depends": [
        'sale',
        'mrp',
        'product_manufacturer',
    ],
    "demo_xml": [],
    "update_xml": [
        "security/product_price.xml",		# always load groups first!
        "security/ir.model.access.csv",        # load access rights after groups
        "company.xml",
        "product.xml",
        "mrp.xml",
    ],
    "auto_install": False,
    "installable": True,
}
