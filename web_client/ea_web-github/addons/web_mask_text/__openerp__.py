# -*- coding: utf-8 -*-
##############################################################################
#
#    Denero Team, Proffestional OpenSource Developers Team.
#    Copyright (C) 2011 - 2013 Denero Team. (<http://www.deneroteam.com>)
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
    'name': 'Web Mask Text Box',
    'category': 'Hidden',
    'description':"""
OpenERP Web Mask Edit Textbox widget module.
===========================
Web Extension for Mask text box is useful tool to validate the user input data with specific format. 
It is based on jQuery extension of Masked Input developed by Josh Bush (see http://digitalbush.com/projects/masked-input-plugin/ ). 

Usage : Add attribute mask with validation format inside the field attribute. 

<field name="phone" mask="(+9 999) 999-99-99" /> 
<field name="ssn" mask="999-99-9999" /> 

""",
    'version': '1.0',
    'author': 'Denero Team <dhaval@deneroteam.com>',
    'website': 'http://www.deneroteam.com',
    'depends': ['web'],
    'update_xml': [
        'res_partner_view.xml',
    ],
    'js': ['static/*/*.js', 'static/*/js/*.js'],
    'css': [],
    'auto_install': False,
    'web_preload': False,
}
