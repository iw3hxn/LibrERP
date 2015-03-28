# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2014 Didotech srl
#    (<http://www.didotech.com>).
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
    'name': 'Italian Localisation Payment Data - Account Didotech',
    'version': '3.0.0.6',
    'category': 'Localisation/Italy',
    'description': """This module adds standard payment terms.


""",
    'author': 'Didotech srl',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'account',
        'l10n_it_account',
        'account_payment_term_month',
    ],
    "data": [
        'data/payment_data.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
