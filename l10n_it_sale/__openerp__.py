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
    'name': 'Italian Localisation - Sale',
    'version': '3.1.1.3',
    'category': 'Localisation/Italy',
    'description': """OpenERP Italian Localization - Sale version

Functionalities:

- Documento di trasporto

""",
    'author': 'OpenERP Italian Community',
    'website': 'http://www.openerp-italia.org',
    'license': 'AGPL-3',
    "depends": [
        'stock', 
        'sale',
        'sale_journal',
        'account', 
        'delivery',
        'sequence_restart',     # ricomincia da 0 le sequenze ogni anno
        'invoice_immediate',    # fattura accompagnatoria
    ],
    "init_xml": [
        "security/ir.model.access.csv",
    ],
    "update_xml": [
        'wizard/assign_ddt.xml',
        'stock/picking_view.xml',
        'stock/carriage_condition_view.xml',
        'stock/transportation_condition_view.xml',
        #'stock/transportation_reason_view.xml',
        'stock/goods_description_view.xml',
        #'stock/transportation_reason_data.xml',
        'stock/goods_description_data.xml',
        'stock/carriage_condition_data.xml',
        'stock/transportation_condition_data.xml',
        'stock/sequence.xml',
        'sale/sale_view.xml',
        'sale/sale_data.xml',
        "security/ir.model.access.csv",
        'partner/partner_view.xml',
        'account/invoice_view.xml',
        'stock/stock.journal.csv',
    ],
    "demo_xml" : [],
    "test": [
        'test/account_tax.xml',
        'test/invoice_emission.yml',
    ],
    "active": False,
    "installable": True
}
