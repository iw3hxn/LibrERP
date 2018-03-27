# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013-2014 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
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
    'name': 'Italian Localisation - Accounting reports',
    'version': '2.1.14.3',
    'category': 'Localisation/Italy',
    'complexity': "easy",
    'description': """Accounting reports for Italian localization - Fattura
        Install report_aero_ooo to be able to output to a format
        different from the one of the template.
    """,
    'author': 'Didotech srl',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'l10n_it_account',
        'report_aeroo',
        'report_webkit',
        'core_extended',
        'invoice_proforma',
    ],
    "data": [
        'reports.xml',
        'template_data_base.xml',
        'wizard/partner_invoice_wizard_view.xml',
        'customer_supplier_report.xml',
        'company_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
