# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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
    'name': 'Proforma Invoice',
    'version': '3.1.1.1',
    'category': 'Account',
    'description': """
    This module covers some requirements regarding the proforma invoice.
    Mostly needed by italian freelancers, layers, notaries and tax preparer.

    Moreover, it adds a sequence to the proforma invoice.
    """,
    'author': 'OpenERP Italian Community',
    'website': 'http://www.openerp-italia.org/',
    'summary': 'Proforma Invoice',
    'depends': ['account'],
    'data': [
        'data/account_data.xml',
        'account_invoice_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
