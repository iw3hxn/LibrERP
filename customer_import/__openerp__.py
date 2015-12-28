# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Ivan Bortolatto (ivan.bortolatto at didotech.com)
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
    'name': 'Framework for import customers',
    'version': '1.1',
    #'category': 'Hidden/Dependency',
    'category': 'Tools',
    'description': """
        This module provide a class import_framework to help importing
        customers data from microsoft(tm) excel
    """,
    "author": "Bortolatto Ivan, Didotech inc.",
    'website': 'http://www.didotech.com',
    'depends': ['base', 'l10n_it_account'],
    'init_xml': [],
    'update_xml': ["wizard/file_import_view.xml"],
    'demo_xml': [],
    'test': [],
    'installable': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
