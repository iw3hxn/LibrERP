# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 credativ Ltd (<http://credativ.co.uk>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Editable ListView Enhanced",
    "description":
        """
        OpenERP Web module which adds facilities to the editable list
        view including fixing column width and row height when
        switching to line editing and enabled arrow key navigation
        between lines and cells.
        """,
    "version": "1.0",
    "author" : "credativ Ltd",
    "website" : "http://credativ.co.uk",
    "category" : "Tools",
    "depends" : ["web"],
    "js": [
        "static/src/js/view_list_editable.js",
    ],
    "auto_install": False,
}
