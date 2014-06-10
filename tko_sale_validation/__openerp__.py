# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Thinkopen Solutions, Lda. All Rights Reserved
#    http://www.thinkopensolutions.com.
#    $Id$
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
    'name': 'Sales Validation',
    'version': '1.002',
    'category': 'Sale',
    'depends': [
        'base',
        'sale',
        'delivery',
    ],
    'author': 'ThinkOpen Solutions',
    'description': '''This module modifies the sale workflow in order to validate sales.
If an order sale ammount is higher than a configured value it must be validated. 
Only users that are part of new group Sale/Validator can authorize a sale order.
The validator can write a message indicating why the sale must be corrected or was canceled, so author knows why.
The author of sale order can correct and propose it to validation again, he has a filter to see refused sales in tree view.
The authorization data and user are registered in database, for future check.''',
    'website': 'http://www.thinkopensolution.com',
    'init_xml': [],
    'update_xml': [
        'security/sale_security.xml',
        'sale_validation_workflow.xml',
        'sale_validation_installer.xml',
        'sale_validation_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,

}
