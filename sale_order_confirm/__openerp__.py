# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2020 Didotech SRL (info at didotech.com)
# All Rights Reserved.
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
    "name": "Extend sale_order",
    "version": "3.32.65.78",
    "category": "Sales Management",
    "description": """This Module, provided user's wizard to confirm/modify sale order.
    It also increases usability on sale order using credit limit amd default payment term
    Is possible to split final invoice in 2 part, credit refund for advanced payment and normal invoice for order

    Look inside 'company' table to configure module.
    If "Need Supervisor Verification after Customer Confirmation" is selected,
    one more confirmation after customer confirmation is required.
    """,
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "depends": [
        'base',
        'res_users_helper_functions',
        'product_bom',
        'l10n_it_base',
        'sale_margin',
        'sale_journal',
        'sale_order_version',
        'web_hide_buttons',
        'product_bom',
        'sale_crm',
        'delivery',
        'account_invoice_extended',
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/confirmation_view.xml',
        'wizard/add_order_version_view.xml',
        'wizard/sale_make_invoice_advance.xml',
        'views/account_fiscal_position_view.xml',
        'views/sale_order_confirm_view.xml',
        'views/sale_order_menu.xml',
        'views/sale_workflow.xml',
        'views/partner_view.xml',
        'views/company_view.xml',
        'views/sale_shop_view.xml',
        'views/res_request_link.xml',
        'views/account_invoice_view.xml',
        'views/crm_lost_reason.xml',
        'views/product_pricelist_view.xml',
    ],
    "demo_xml": [],
    "installable": True,
    "active": False,
}
