# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016-2019 Didotech SRL
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
    'name': 'export_primanota_teamsystem',
    'version': '3.2.9.2',
    'category': 'Accounting & Finance',
    'description': """
    Export Primanota in TRAF2000 format accepted by TeamSystem program
    """,
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'base',
        'account',
        'l10n_it_account',
        'l10n_it_ricevute_bancarie',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/export_primanota.xml',
        'views/account_view.xml',
        'views/account_payment_term_view.xml',
        'views/account_journal_view.xml',
        'views/account_invoice_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True,
    'external_dependencies': {}
}