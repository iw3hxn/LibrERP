# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Didotech SRL (<http://www.didotech.com>).
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
    'name': 'Italian Localisation - Account Didotech',
    'version': '3.1.1.5',
    'category': 'Localisation',
    'description': """This module add res.bank for ri.ba. in partner

""",
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'account',
        'l10n_it_account',  # serve per onchange dentro account.invoice
        'account_invoice_entry_date'
    ],
    "data": [
        'security/security.xml',
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
