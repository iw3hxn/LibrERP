# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    26-APR-2012 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1.17, USA.
#
###############################################
{ "name"         : "Variant of field type one2many and many2many for sorted associations"
, "version"      : "1.0"
, "author"       : "Swing Entwicklung betrieblicher Informationssysteme GmbH"
, "website"      : "http://www.swing-system.com"
, "description"  : """
Variant of field type one2many for sorted associations

Usage:

| import one2many_sorted
| ...
|    _columns = \
|        { 'partner_ids'  : one2many_sorted.one2many_sorted
|            ( 'res.partner'
|            , 'parent_id'
|            , 'Sorted Partner List'
|            , order='name.upper(), title'
|            , search=[('is_company', '=', 'False')]
|            , set={'is_company' : False}
|            )
|        }
| ...

In the example above, the primary sort criteria is "name" (not case-sensitive), the secondary is "title".
Only partners that are physical persons (not is_company) are selected - and only those can be added.

Another possibility is to define a text-property with naming convention "<obj>.<field>.order" 
(in the example above this would be "res.partner.parent_id.order").
The value of this property is the sort criteria.

The advantage of properties is, that they can by company-individual.

A third possibility is to hand over a "context" key named "one2many_sorted_order" that contains the name of a property.

If no "context" key is found, then the property with the naming convention is taken.
If no property is defined, the programmed sort order is taken.
Otherwise no sorting takes place.

many2many_sorted has a similar syntax but without search feature.

Note that it works on translated term, not only the text stored in the DB !


"""
, "category"     : "Tools"
, "depends"      : ["base"]
, "init_xml"     : []
, "demo"         : []
, "update_xml"   : []
, "test"         : []
, "auto_install" : False
, "installable"  : True
, 'application'  : False
}
