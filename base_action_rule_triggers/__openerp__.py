# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2011-2012
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
    'name': 'Automated Action Rules Trigger Extensions',
    'version': '6.1.1',
    'category': 'Sales Management',
    'description': """Extensions to the Automated Actions module base_action_rule.

Actions can be triggered from evaluated expression, using values from dictionaries 'old' and 'new'
  new - is the dictionay passed to the create/write method, therefore. It contains _only_ the fields to write.
  old - on create is an empty dict {} or None value; on write contains the all object values before the write is executed, as given by the read() method.
It's recommended to access these dictionaries using teh get() method.
Example, check if document was reopened: old.get('state') != 'open' and new.get('state') == 'open'

The following boolean flags are also available for the expressions:
  creating, inserting
  writing, updating
Example, check if responsible changed: updating and old.get('user_id') != new.get('user_id')
""",
    'author': 'Daniel Reis',
    'website': 'https://launchpad.net/~dreis-pt',
    'depends': [
        'base_action_rule',
        'crm', #crm_action_rule
        'email_template',
    ],
    'init_xml': [],
    'update_xml': ['base_action_rule_view.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
