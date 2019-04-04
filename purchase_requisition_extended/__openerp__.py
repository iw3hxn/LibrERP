# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2018 Carlo Vettore (carlo.vettore at didotech.com)
#
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


{
    "name": "Purchase Requisition Extended",
    "version": "3.1.5.11",
    "author": "Andrei Levin",
    "category": "Sales & Purchases",
    "description": '''
        This module make some usability changes,
        add possibility to make a request for quotations to all suppliers at once
        or to prefered suppliers (with the lower sequence code) only
    ''',
    "depends": [
        "base",
        'purchase_requisition',
        'purchase_no_gap',
    ],
    "data": [
        'security/purchase_security.xml',
        'wizard/purchase_requisition_partner_view.xml',
        'views/purchase_requisition_view.xml'
    ],
    "active": False,
    "installable": True,
}
