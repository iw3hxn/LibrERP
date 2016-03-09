# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014 Didotech SRL (<http://didotech.com>).
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
    'name': 'Stock picking extended',
    'version': '3.22.20.26',
    'category': 'Others',
    'description': """LibrERP - Stock picking extension

Functionalities:
    - different shipping address for consignement order
    - correct wkfl in stock, sale, invoice
    - add user for stock_journal
""",

    'author': 'Didotech srl',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'stock', 
        'sale',
        'sale_journal',
        'account', 
        'delivery',
        'sequence_restart',     # ricomincia da 0 le sequenze ogni anno
        'sale_margin',
        'purchase',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/journal_security.xml',
        'stock/picking_view.xml',
        'stock/carriage_condition_view.xml',
        'stock/transportation_condition_view.xml',
        'stock/goods_description_view.xml',
        'sale/sale_view.xml',
        'sale/sale_data.xml',
        'partner/partner_view.xml',
        'stock/stock.journal.csv',
        'stock/stock_journal_view.xml',
        'purchase/purchase_view.xml',
        'company/company_view.xml',
    ],
    "demo": [],
    "test": [
    ],
    "active": False,
    "installable": True
}
