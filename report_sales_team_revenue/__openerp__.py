# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016-2017 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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
    'name': 'report_sales_team_revenue',
    'version': '3.2.7.1',
    'category': 'Accounting & Finance',
    'description': """
    Export revenue on month basis for selected Sales Team
    """,
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'base',
        'crm',
        'sale_commission'
    ],
    "data": [
        # 'security/ir.model.access.csv',
        'wizard/export_sales_team_report_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True,
    'external_dependencies': {
        'python': [
            'xlrd',
        ]
    }
}
