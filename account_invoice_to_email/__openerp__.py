# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright © 2019 Didotech SRL (<http://www.didotech.com>).
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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Email template extension',
    'version': '1.0.0.0',
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'category': 'Marketing',
    'description': '''
        Module that extends the normal email_template to autmatically add the fields in the email creation
    ''',
    'depends': ['email_template'],
    'demo_xml': [],
    'init_xml': [
    ],
    'data': [
        'data/email_template_extension_data.xml',
    ],
    'auto_install': False,
    'installable': True,
}
