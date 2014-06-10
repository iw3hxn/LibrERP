# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
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
    'name': 'Base Contact extension',
    'version': '6.1.0.2',
    'category': 'Base',
    'description': """
This module fix the problem of name and mobile field entry at the creation time of res.partner.address
Due to base_contact changes, if res.partner.address does not set contact_id set at the time of creation or updation, value with both field will be set to null.
This module will fix that problem.
""",
    'author': 'Denero Team',
    'website': 'http://www.deneroteam.com',
    'depends': ['base_contact'],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
