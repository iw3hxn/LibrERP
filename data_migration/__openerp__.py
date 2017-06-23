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

{
    'name': 'Data migration import',
    'version': '3.12.59.20',
    'category': 'Tools',
    'description': """
        This module gives a possibilitie to import products and partners
        from CSV/Excel/OpenOffice formatted files.

        When option 'strict' is selected, partner will be searched on every
        field in PARTNER_SEARCH and if in doubt nothing will be changed or
        updated. It is usefull to use this mode to be shure that nothing will
        be overwritten.
    """,
    "author": "Didotech SRL",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'purchase',
        # 'partner_subaccount',
        # 'l10n_it', not needed, pdc is installed
        # 'l10n_it_account',
        'core_extended',
        'email_message_custom'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/file_import_view.xml',
        'wizard/sale_order_state_view.xml',
        'partner_template_view.xml'
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [
            'xlrd',
        ]
    }
}
