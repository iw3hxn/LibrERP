# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Associazione OpenERP Italia
#    http://www.openerp-italia.org> 
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
    'name': 'Account Invoice entry Date',
    'version': '3.3.12.8',
    'category': 'Generic Modules/Accounting',
    'description': """This module allows to specify the date to be used by the move created while confirming (supplier) invoice""",
    'author': 'OpenERP Italian Community',
    'website': 'http://www.openerp-italia.org',
    'license': 'AGPL-3',
    "depends": [
        'account',
        'account_payment_term_month',  # for update payment with tax in function compute
        'account_due_list'
    ],
    "data": [
        'views/invoice_view.xml'
    ],
    "demo": [],
    "active": False,
    "installable": True
}
