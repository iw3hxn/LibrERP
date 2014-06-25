# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Didotech SRL (<http://didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Italian Localisation - Account Didotech',
    'version': '2.0.0.0',
    'category': 'Localisation/Italy',
    'description': """Fix analytic view adding supplier and customer invoice nr
""",
    'author': 'Didotech',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'account',
        'analytic',
    ],
    "data": [
        'data/analytic_line_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
