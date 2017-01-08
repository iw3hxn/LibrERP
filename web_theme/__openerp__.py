# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Poiesis Consulting (www.poiesisconsulting.com).
#    Autor: Nicolas Bustillos
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
    'name': 'Web Theme',
    'version': '1.0.1',
    'description': """Allows to assign a logo and and color set per Company
    Configuration
    - After installation, go to Company Form to upload an image file and assign a predefined color set
    - You can create your own color profile by selecting 'Create...' from the Color Set combobox. Just assign a name and specify the required colors in hex format (e.g. #F09090)
    """,
    'category': 'Web',
    'author': 'Poiesis Consulting',
    'website': 'http://www.poiesisconsulting.com',
    'depends': ['base','web'],
    'js': ['static/src/js/theme.js'],
    'init_xml': ['theme_data.xml'],
    'update_xml': [
        'company_view.xml',
        'security/ir.model.access.csv',
    ],
    'images': [
        'images/company.png',
        'images/schema.png'
    ],
    'installable': True,
}
