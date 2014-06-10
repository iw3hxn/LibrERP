# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Enapps LTD (<http://www.enapps.co.uk>).
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
    "name": "Web Tabs",
    "category": "Tools",
    "description":
        """
        Tabs for main windows
        """,
    "version": "0.1",
    "depends": [],
    "js": [
        "static/js/chrome.js",
        "static/js/ui.tabs.closable.min.js",
    ],
    "css": [],
    "qweb": [
        "static/xml/tabs.xml",
    ],
    'auto_install': True,
    'web_preload': False,
}
