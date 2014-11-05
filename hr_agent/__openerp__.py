# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012-2014 didotech SRL (info at didotech.com)
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
    "name": "Hr Agent - Extended management of human resources for Managing Commercial's Agents.",
    'version': '2.0.3.0',
    'category': 'Generic Modules/Human Resources',
    "description": """This Module, extended management of human resources for Managing Commercial's Agents.""",
    "author": "Bortolatto Ivan, Didotech.com",
    "depends": [
        "base",
        "l10n_it_base",
        #"l10n_it",
        "product",
        "sale",
        "hr",
        "account_payment",
        "account_voucher",
        "sale_order_confirm",
    ],
    "init_xml": [
        "hr_agent_sequence.xml"
    ],
    "update_xml": [
        "res_partner_zone_view.xml",
        "hr_agent_view.xml",
        "security/agent_security.xml",
        "security/ir.model.access.csv",
        "report/hr_agent_report_view.xml"
    ],
    "demo_xml": [],
    "installable": True,
    "active": False,
}
