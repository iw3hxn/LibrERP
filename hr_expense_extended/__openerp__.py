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
    "name": "HR Expense Extended",
    "version": "2.8.17.10",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": 'Human Resources',
    "description": """
        Module extends functionality of the hr_expense module:
            - expense line will also create account_analytic_line
            - if set, report will not show more than max_work_hours a day
            - expenses can be added to task
    """,
    "depends": [
        'base',
        'hr_expense',
        'task_time_control',
        'hr_timesheet',
        'hr_timesheet_sheet',
        'mrp',
        'work_order',
        'project',
        'task_time_control',
        'res_users_helper_functions',
        'res_user_signature',
    ],
    "data": [
        'views/hr_expense_view.xml',
        'views/project_view.xml',
        'views/hr_employe_menu.xml',
        'views/hr_employe_view.xml',
        'views/task_time_control_wizard_view.xml',
        'report/reports.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizards/export_project_cost_view.xml',
    ],
    "active": False,
    "installable": True,
        'external_dependencies': {
        'python': [
            'dateutil',
        ]
    }
}
