# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014-2018 Didotech srl (<http://www.didotech.com>).
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
    "version": "3.19.46.37",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": "Sales Management",
    "description": """
        Module permits to assign product costs to a project

        This module create:
        a) project if a sale order is create and shop required a project
        b) project.task for each service sell in sale.order
        c) is possible to create multiple task in this mode:
            on res.company set the unit time for project (example Hour)
            create a product kit with inside a service (to produce) with different unit of measure (example day)
            sell it
        d) is possible to create a map of field from sale order line to task


        NOTE: This module is incompatible with module sale_analytic_plans
    """,
    "depends": [
        'base',
        'stock',
        'dt_product_serial',
        'project',
        'mrp',
        'mrp_bom_standard_price',
        'sale_order_confirm',
        'project_timesheet',
        'task_time_control',
        'project_extended',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/stock_picking_view.xml',
        'views/sale_order_view.xml',
        'views/res_request_link.xml',
        'views/account_analytic_line_view.xml',
        'data/company_data.xml',
    ],
    "active": False,
    "installable": True,
}
