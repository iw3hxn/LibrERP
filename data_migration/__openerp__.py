# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Didotech srl (http://www.didotech.com)
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
#

{
    'name': 'Data migration import',
    'version': '2.2.19.4',
    'category': 'Tools',
    'description': """
        This module gives a possibilitie to import products and partners
        from excel formatted files.
        
        When option 'strict' is selected, partner will be searched on every field in PARTNER_SEARCH and if in doubt
        nothing will be changed or updated. It is usefull to use this mode to be shure that nothing will be overwritten.
    """,
    "author": "Didotech SRL",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'purchase',
        #'partner_subaccount',
        #'l10n_it', not needed, pdc is installed by default and can differ from this one
        'l10n_it_account',
        'core_extended'
    ],
    'init_xml': [],
    'update_xml': [
        "wizard/file_import_view.xml"
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [
            'xlrd',
        ]  
    }
}
