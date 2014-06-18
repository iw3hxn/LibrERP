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
    "name": "WYSIWYG Wiki in HTML",
    "version": "0.0.1",
    "author": "Matmoz d.o.o. (Didotech Group)",
    "website": "https://cloud.matmoz.si/f/9e3e344c85/",
    "category": "Knowledge Management",
    "description":
    """
        The Wiki is composed in HTML (WYSIWYG with ckeditor) instead of wiki format.
        Screenshot's link under the author's webpage.
    """,
    "depends":
            [
                "wiki",
                "base",
                "web_wysiwyg",
                "web_display_html"
            ],
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
        "html_wiki.xml"
    ],
    "installable": True
}
