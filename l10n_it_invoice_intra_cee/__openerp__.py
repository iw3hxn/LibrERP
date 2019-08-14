# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>)
#    Copyright (C) 2014 Didotech srl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Invoice Intra CEE",
    'version': '3.2.12.5',
    'category': 'Account',
    'description': """Manage Invoice for Intra CEE supplier""",
    'author': 'CoOpenERP <info@coopenerp.it>, Didotech srl <info@didotech.com>',
    'website': 'http://www.coopenerp.it, http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'base',
        'account',
        'account_voucher',
        'l10n_it_account',
        'account_payment_term_month',
    ],
    "data": [
        'account/account_view.xml',
        'account/account_data.xml',
    ],
    "demo": [],
    "test": [
        'test/invoice_reverse_charge.yml',
    ],
    "active": False,
    "installable": True
}
