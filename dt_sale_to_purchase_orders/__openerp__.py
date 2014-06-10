# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-Today OpenERP SA (<http://www.openerp.com>).
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
    'name' : 'Sale to Purchase Order',
    'version': '1.0',
    'author': 'Sistemas ADHOC',
    'website': 'http://www.sistemasadhoc.com.ar/',
    'depends' : ["sale", "purchase"],
    'category' : 'Sale Management',
    'description': '''This module create a wizard asociated to an action on Sale
Orders. This wizard generates a Purchase Order from the information of the Sale Order.
    ''',
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : ['wizard/generate_purchase_order_wizard.xml'],
    'active': False,
    'installable': True
}
