# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2012 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Copyright (C) 2014 Didotech s.r.l. (<http://www.didotech.com>).
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
    "name": "VAT on payment",
    "version": "2.0.2.1",
    'category': 'Generic Modules/Accounting',
    "depends": ["account_voucher_cash_basis"],
    "author": "Didotech srl",
    "description": """
See 'account_voucher_cash_basis' description.

To activate the VAT on payment behaviour, this module adds a checkbox on
invoice form, on company form and on fiscal position form: 'Vat on payment'

    """,
    'website': 'http://www.didotech.com',
    'data': [
        'account_view.xml',
        'fiscal_position_view.xml',
        ],
    'demo': [],
    'installable': True,
    'active': False,
}
