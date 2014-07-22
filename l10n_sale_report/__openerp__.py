# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
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
    'name': 'Localized Aeroo Sale reports',
    'version': '2.0.2.3',
    'category': 'Localisation/Reporting',
    'description': """
This module sets the environment for the localized aeroo templates,
which are installed with a separated module.
=====================================================================

Install report_aero_ooo to be able to have output in a format
different from the one of the template and don't forget to install the localized
reports for your country - l10n_(country code)_sale_reports
    """,
    'author': 'OpenERP Italian Community',
    'website': 'http://www.openerp-italia.org',
    'license': 'AGPL-3',
    "depends": [
        'l10n_it_sale',
        'report_aeroo',
        'stock',
        'l10n_it_account_report'
    ],
    "init_xml": [
    ],
    "update_xml": [
    ],
    "demo_xml": [],
    "active": False,
    "installable": True
}
