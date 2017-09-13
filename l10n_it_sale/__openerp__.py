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
    'version': '3.10.20.22',
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
        'c2c_sequence_fy',       # ricomincia da 0 le sequenze ogni anno
        'invoice_immediate',     # fattura accompagnatoria
        'sale_order_confirm',
        'core_extended',
        'stock_picking_filter',  # for have date from and date to on picking filter for ddt date
        'sequence_recovery',
    ],
    "data": [
        'wizard/assign_ddt.xml',
        'wizard/confirmation_view.xml',
        'wizard/stock_partial_picking.xml',
        'views/picking_view.xml',
        'views/stock_journal_view.xml',
        'views/sale_order_view.xml',
        'views/stock_journal_view.xml',
        'views/delivery_grid_view.xml',
        'data/sequence.xml',
        'data/goods_description_data.xml',
        'data/carriage_condition_data.xml',
        'data/transportation_condition_data.xml',
    ],
    "demo": [],
    "test": [],
    "active": False,
    "installable": True
}
