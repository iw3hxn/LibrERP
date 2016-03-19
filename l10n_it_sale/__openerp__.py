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
    'version': '3.8.13.16',
    'category': 'Localisation/Italy',
    'description': """OpenERP Italian Localization - Sale version

Functionalities:

- Documento di trasporto
- CIG, CUP nella conferma ordine cliente

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
        'sequence_restart',      # ricomincia da 0 le sequenze ogni anno
        'invoice_immediate',     # fattura accompagnatoria
        'sale_order_confirm',
        'core_extended',
        'stock_picking_filter',  # for have date from and date to on picking filter for ddt date
    ],
    "data": [
        'wizard/assign_ddt.xml',
        'wizard/confirmation_view.xml',
        'wizard/stock_partial_picking.xml',
        'stock/picking_view.xml',
        'stock/sequence.xml',
        'stock/stock_journal_view.xml',
        'sale/sale_order_view.xml',
        'stock/goods_description_data.xml',
        'stock/carriage_condition_data.xml',
        'stock/transportation_condition_data.xml',
    ],
    "demo": [],
    "test": [],
    "active": False,
    "installable": True
}
