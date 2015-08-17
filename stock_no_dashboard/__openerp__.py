# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Akretion LTDA.
#    authors: Raphaël Valyi
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
    'name': 'Stock No Dashboard',
    'version': '1.1',
    'category': 'Generic Modules/Stock',
    'description': """
This module disable the stock dashboard, which makes OpenERP fast again with the web-client and real production data that otherwise makes the dashboard very slow and that break your navigation.
Notice that the dashboard is still available through it's dedicated menu.""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'init_xml': [],
    'update_xml': ['stock_view.xml'],
    'demo_xml': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
