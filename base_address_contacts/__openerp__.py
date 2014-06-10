# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - TODAY Deneroteam. (<http://www.deneroteam.com>)
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
    'name': 'Base Address Contact',
    'version': '6.1.5',
    'category': 'Base',
    'description': """
This module allows you to manage your contacts
==============================================

It lets you define:
    * contacts unrelated to a partner,
    * contacts working at several addresses (possibly for different partners),
    * contacts with possibly different functions for each of its job's addresses
""",
    'author': 'Denero Team',
    'website': 'http://www.deneroteam.com',
    'depends': ['base'],
    'update_xml': [
        'res_partner_address_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
