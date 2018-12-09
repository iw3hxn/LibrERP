# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2014 Didotech srl (www.didotech.com).
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
    'name': 'Assets Management',
    'version': '2.8.17.17',
    'depends': [
        'report_webkit',
        'l10n_it_account',
        'l10n_it_partially_deductible_vat',
    ],
    'author': 'Odoo & Noviat & Didotech',
    'description': """
Financial asset management.
===========================

This Module manages the assets owned by a company. It will keep
track of depreciation's occurred on those assets. And it allows to create
accounting entries from the depreciation lines.

The depreciation table can be calculated based upon different Time Methods\n
- Number of Years
- Number of Depreciations
- Ending Date
- Percent

This Module can be used for Financial Assets Management (via Time Method 'Number of Years')
as well as for Deferred Cost/Income and Cost/Income Spreading purposes (via Time Methods
'Number of Depreciations' and 'Ending Date'.

The full asset life-cycle is managed (from asset creation  up to asset removal).

Assets can be created manually as well as automatically (via the creation of an accounting entry on the asset account).
Assets values can be purchased/sold from purchase/sale invoices taking the specific asset to be changed.
Assets values can be increased/decreased from account moves taking the specific asset to be changed.

Excel based reporting is available via the 'account_asset_report_xls' module (cf. http://odoo.apps.com).
Legal report for Italy is available.

    """,
    'website': 'http://www.odoo.com',
    'category': 'Accounting & Finance',
    'sequence': 32,
    'demo': ['account_asset_demo.xml'],
    'test': [
        'test/account_asset_demo.yml',
        'test/account_asset.yml',
        'test/account_asset_wizard.yml',
    ],
    'data': [
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        #'wizard/account_asset_change_duration_view.xml', #TODO test functionality before activate
        'wizard/wizard_asset_compute_view.xml',
        'wizard/account_asset_remove_view.xml',
        'account_asset_view.xml',
        'account_view.xml',
        'account_asset_invoice_view.xml',
        'reports.xml',
        'report/account_asset_report_view.xml',
        'report/print_asset_report.xml',
        'wizard/wizard_asset_confirm.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
