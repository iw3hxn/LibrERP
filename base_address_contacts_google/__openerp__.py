# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 - TODAY DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011 - TODAY Didotech Inc. (<http://www.didotech.com>)
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
    'name': 'Google Contact',
    'version': '2.0.2.0',
    'category': 'Generic Modules',
    'description': """
        Synchronize contacts with Google Contacts. Based on a work of Roberto Lizana (www.trey.es)
    """,
    'author': 'Carlo Vettore ',
    'website': 'www.didotech.com',
    'depends': [
        'base',
        'base_address_contacts'
    ],
    'data': [
        'contact_wizard.xml',
        'contact_view.xml',
        'contact_data.xml',
    ],
    'demo_xml': [],
    'installable': True,
}
