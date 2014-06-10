# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright: (C) 2013 Matmoz d.o.o.
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
    "name": "Slovenian - Minimal Accounting",
    "version": "1.4",
    "author": "Matmoz d.o.o.",
    "website": "http://www.matmoz.si",
    "category": "Localization/Account Charts",
    "description": "Slovene account chart 2013 - openerp 6.1 version",
    "depends":
        [
        'base_vat',
        'account',
        'account_chart',
        'base_iban',
        'partner_subaccount',
        'l10n_it_base',
        'l10n_it_account',
        'base_ordered',
        'base_vat_unique'
        ],
    "description": """
Slovene account chart 2013 - personalized for partner_subaccount module
================================================

    """,
    "license": "AGPL-3",
    'init_xml': [],
    'update_xml': [
        'data/account.account.template.csv',
        'data/account.tax.code.template.csv',
        'account_chart.xml',
        'data/account.tax.template.csv',
        'data/account.fiscal.position.template.csv',
        'data/account.fiscal.position.tax.template.csv',
        'l10n_chart_si.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'auto_install': False,
}
