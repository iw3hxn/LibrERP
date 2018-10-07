# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2012-2014 Didotech srl (info@didotech.com)
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
    'name': 'Asset Logistic Management',
    'version': '3.4.24.15',
    'category': 'Generic Modules/Asset Logistic Management',
    'description': """
        A generic module to manage company asset and its movements.
        
        Attention!
        For some unknown reason this module sets Location "Output" to type "Internal Location".
    """,
    'author': 'Dhaval Patel & Andrei Levin',
    'depends': [
        'base',
        'account_asset',
        'product',
        "hr",
        "resource",
        'stock',
        "project_long_term",
        'hr_auto',
#        'project_place',
        'product_manufacturer',
        'product_code_category',
        'dt_product_serial',
        'hr_sim',
        'web_hide_buttons'
    ],
    'data': [
        'security/assets_security.xml',        # always load groups first!
        'security/ir.model.access.csv',        # load access rights after groups
        'asset_view.xml',
        'asset_data.xml',
        'asset_location_data.xml',
        'views/asset_inherit_view.xml',
        'views/stock_view.xml',
        'asset_configuration_view.xml',
        'wizard/asset_move_create.xml',
        'wizard/asset_assign_category.xml',
        'wizard/asset_document_expiry_bymonth_view.xml',
        'report/asset_move/reports.xml',
    ],
    'demo': [
        'asset_view_demo.xml'
    ],
    'installable': True,
    'active': False,
}
