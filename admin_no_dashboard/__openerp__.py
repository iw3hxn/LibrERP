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
    'name': 'Sale No Dashboard',
    'version': '1.0',
    'category': 'Generic Modules/Sale',
    'description': """
This module disable the admin dashboard, which makes OpenERP fast again with the web-client and real production data that otherwise makes the dashboard very slow and that break your navigation.
Notice that the dashboard is still available through it's dedicated menu.""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['sale'],
    'init_xml': [],
    'update_xml': ['admin_view.xml'],
    'demo_xml': [],
    'installable': True,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
