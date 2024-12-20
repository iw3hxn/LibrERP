#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
#"license" : "AGPL-3",
{
    "name": "This module inherits standard price field in mrp.bom", 
    "version": "3.4.2.8",
    "author": "Vauxoo, Didotech",
    "category": "Generic Modules", 
    "description": """This module inherits standard price field in mrp.bom and also sequence
    """, 
    "website": "https://www.didotech.com",
    "license": "", 
    "depends": [
        "product", 
        "mrp",
        "product_bom"
    ], 
    "demo": [], 
    "data": [
        "views/mrp_bom_view.xml",
        "views/mrp_routing_view.xml",
        "views/mrp_routing_workcenter_view.xml",
        "views/product_product_view.xml",
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}
