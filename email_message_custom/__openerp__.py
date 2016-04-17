# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Matmoz d.o.o. (<http://www.matmoz.si>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Email message customized",
    "version": "3.0.5.2",
    "author": "Matmoz d.o.o. (Didotech Group)",
    "website": "http://www.matmoz.si",
    "category": "Vertical Modules/Parametrization",
    "description":
    """
        Customized email message, unlocked some fields,
            html wysiwyg and WYSIWYG editor for emails
    """,
    "depends":
            [
                "mail",
                "base",
                "web_wysiwyg",
                "web_display_html"
            ],
    "data": [
        "email_wysiwyg_data.xml",
        "tree_view.xml"
    ],
    "active": False,
    "installable": True,
    "auto_install": True,
}
