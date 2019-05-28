# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Didotech srl (info at didotech.com)
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
    'name': 'Show modules to upgrade',
    'version': '3.0.1.5',
    'category': 'Tools',
    'description': """
        Modules add a column that shows if module should be upgraded.
        It also adds a button that shows which modules should be upgraded
    """,
    "author": "Didotech srl",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
    ],
    'data': [
        "views/module_view.xml"
    ],
    'test': [],
    'installable': True,
    'auto_install': True,
}
