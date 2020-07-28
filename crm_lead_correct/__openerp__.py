# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2020 Didotech SRL (info at didotech.com)
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
    'name': 'Module corrects a bug in crm_lead, when creating a partner. Parameter customer is True.',
    'version': '4.12.30.30',
    'category': 'Customer Relationship Management',
    'description': """A module for crm. Extended by Didotech """,
    "author": "Didotech SRL",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'crm',
        'base_address_contacts',
        'l10n_it_base',
        'sale_crm',
        'sale_order_confirm',
        'res_users_helper_functions',
        'web_support',  # because of field email_from created there
    ],
    'init_xml': [],
    'update_xml': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
        'views/crm_lead_menu.xml',
        'views/crm_opportunity_view.xml',
        'views/crm_meeting_view.xml',
        'views/crm_meeting_menu.xml',
        'views/crm_case_categ_view.xml',
        'views/res_partner.xml',
        'views/crm_lead_sequence.xml',
        'views/crm_phonecall_view.xml',
        'views/crm_super_calendar_view.xml',
        # 'crm_lead_data.xml',
        'views/sale_order_view.xml',
        'views/sale_shop_view.xml',
        'report/crm_meeting_report_by_province.xml',
        'wizard/crm_meeting_by_province_view.xml',
        'wizard/crm_lead_to_opportunity_view.xml',
        'wizard/crm_partner_to_opportunity_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
