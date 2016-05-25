# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Stock Out Alert
#    Copyright (C) 2013 Enterprise Objects Consulting
#                       http://www.eoconsulting.com.ar
#    Authors: Mariano Ruiz <mrsarm@gmail.com>
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
    "name" : "Stock Out Alert",
    "description":"""
Report 'Products Out of Stock', allows you to check the stock availability
based on the product stock rules.

Add a scheduler launched automatically every night by OpenERP,
and the result is send by email to all user in
'Warehouse Management / Stock Monitor' group.
""",
    "version" : "0.1.1",
    "author" : "Enterprise Objects Consulting",
    "website" : "http://www.eoconsulting.com.ar",
    "category" : "Warehouse Management",
    "depends" : ["stock", "procurement", "purchase"],
    "data" : [ "scheduler_data.xml", 'wizard/stock_compute_out_view.xml' ],
    "images" : [ 'images/stock_out_alert_report.png','images/stock_out_alert_wizard.jpeg',],
    "active": False,
    "installable": True
}
