# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Didotech SRL (info at didotech.com)
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
    "name": "Hide Tax on Product Form",
    "version": "3.0.0.1",
    "category": "Accounting",
    "description": """This Module, provided user's wizard for confirm/modify sale order.
    Also increasu usability on sale order using credit limit amd default payment term
    """,
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "depends": [
        "base",
        "product",
        "account",
    ],
    "init_xml": [],
    "update_xml": [
        'product_view.xml',
        'account_view.xml',
        'company_view.xml',
    ],
    "demo_xml": [],
    "installable": True,
    "active": False,
}
