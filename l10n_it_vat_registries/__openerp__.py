# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
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
    'name': 'Italian Localisation - VAT Registries',
    'version': '2.1.7.9.4',
    'category': 'Localisation/Italy',
    'description': """Accounting reports for Italian localization - VAT Registries\n
    http://wiki.openerp-italia.org/doku.php/moduli/l10n_it_tax_journal""",
    'author': 'OpenERP Italian Community',
    'website': 'http://www.openerp-italia.org',
    'license': 'AGPL-3',
    "depends": [
        'report_webkit',
        'l10n_it_base',
        'l10n_it_partially_deductible_vat'
    ],
    "data": [
        'reports.xml',
        'wizard/print_registro_iva.xml',
        'views/account_view.xml',
    ],
    "demo": [
        'demo/account_tax.xml',
    ],
    'test': [
         'test/tax_computation.yml',
         'test/report_registries.yml',
    ],
    "active": False,
    "installable": True
}
