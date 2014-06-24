# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP Module
#    
#    Copyright (C) 2012+ BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
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
    'name' : 'Group Pickings',
    'version' : '2.0.0.0',
    'author' : 'Marco Dieckhoff, BREMSKERL',
    'website' : 'www.bremskerl.com',
    'depends' : ['stock'],
    'category' : 'Warehouse',
    'description': """
This module allows you to group stock pickings (Incoming Shipments, Delivery Orders, Internal Moves).

Only type (in, out, internal) and address must be the same to allow grouping,
in order to print a single set of delivery papers for multiple transactions.

    """,
    'demo' : [],
    'data' : ['security/ir.model.access.csv',
                    'view/picking_group_view.xml',
                    'view/stock_view.xml'],
    'active': False,
    'installable': True
}
