# -*- encoding: utf-8 -*-
##############################################################################
#
#    Merge Picking up to v5 of OpenERP was written by Axelor, www.axelor.com
#    Copyright (C) 2010-2011 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff (complete rewrite)
#    Copyright (C) 2013 Didotech srl (<http://www.didotech.com>).
#    (Various adjustments, PEP8 compliance)
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
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
    'name': 'Merge Picking',
    'version': '1.0.0',
    'author': 'BREMSKERL, Didotech srl',
    'website': 'www.didotech.com',
    'depends': [
        'stock'
    ],
    'category': 'Warehouse',
    'description': """
This module allows you to manually merge stock pickings (Incoming Shipments, Delivery Orders, Internal Moves).
    """,
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [
        'view/stock_view.xml',
        'wizard/merge_picking_view.xml'
    ],
    'active': False,
    'installable': True
}
