# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011-2013 Didotech Inc. (<http://www.didotech.com>)
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
    'name': 'Generic Module/Project Place and Plants',
    'version': '2.0.2.2',
    'category': 'Generic Modules',
    'description': """
        A generic module to manage project place and plants on Project.
    """,
    'author': 'Deneroteam - Didotech SRL',
    'website': 'http://www.didotech.com',
    'depends': [
        'hr',
        'project',
        'stock',
        'l10n_it_base',
        'l10n_it_sale',
        'base_address_contacts',
        'web_hide_buttons',
    ],
    'init_xml': [
        'security/place_security.xml',
        'security/ir.model.access.csv',
        'project_place_view.xml',
        'project_place_sequence.xml'
    ],
    'update_xml': [
        'security/place_security.xml',
        'security/ir.model.access.csv',
        'project_place_view.xml',
        'project_place_sequence.xml'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
