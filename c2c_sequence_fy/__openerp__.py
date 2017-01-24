# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp (<http://www.camptocamp.at>)
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
    'name': 'Sequence Financial Year Extension fy (for v61 and above',
    'version': '3.0.4.0',
    'category': 'Accounting & Finance',
    'description': """
This module adds 
* monthly sequences for journals
* "fy", "stn", "stc" and "jn" as placeholder for prefix and suffix.

* creation rules for missing sequences in ir_sequence_type and account journal
   if a not existing sequence is requested it will be created on the fly.
   * if no prefix pattern is defined in sequence-codes, a name will be created using 
     the first characters of each word of then name of the sequence-code
     Example "Account Invoice In" will be "AAI-"

* "fy" (fiscal year)
  This allows contiguous numbering per fiscal year.
  This sequence code will be used to format the start date of the fiscal year 
  for the placeholder 'fy' defined for sequences as prefix and suffix.
  Example a fiscal year starting on March 1st with a sequence code %Ya will generate 2011a.
  This allows to handle multiple fiscal years per calendar year and fiscal years not matching calendar years easily.

* "stn" (sequence-type-name)
  This allows to use the (abbreviated) sequence-code name as placeholder.

* "stc" (sequence-type-code)
  This allows to use the (abbreviated) sequence-code code as placeholder.

* "jn" (journal-name)
  This allows to use the (abbreviated) journal name as placeholder.
  
If no prefix/suffix is specified, the prefix/suffix of the sequence-code is used. 

This module is a prerequisite to automatically generated new fiscal years, periods and associated sequences 
using '(fy)' instead of hard coding.

* Configuration wizard:
  During configuration you may choose to replace all '(year)' prefix and suffix occurrences by '(fy)'.
""",
    'author': 'Camptocamp',
    'depends': [
        'account'
    ],
    'update_xml': [
        'views/ir_sequence_view.xml',
        'views/account_fiscalyear_view.xml',
        'views/ir_sequence_type_view.xml',
        'views/ir_sequence_installer_view.xml',
        'views/account_view.xml',
        'security/ir.model.access.csv'
    ],
    'demo_xml': [],
    'installable': True,
    'active': False
}
