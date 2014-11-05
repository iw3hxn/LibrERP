# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
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
    "name": "Job Order management",
    "version": "3.10.21.15",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": "Sales Management",
    "description": """
        Module permits to assign product costs to a project
        
        NOTE: This module is incompatible with module sale_analytic_plans
    """,
    "depends": [
        'base',
        'stock',
        'dt_product_serial',
        'project',
        'sale_order_confirm',
        'project_timesheet',
        'task_time_control',
        'project_extended',
    ],
    "init_xml": [],
    "update_xml": [
        'security/ir.model.access.csv',
        'res_company_view.xml',
        'stock_picking_view.xml',
        'sale_order_view.xml',
    ],
    "active": False,
    "installable": True,
}
