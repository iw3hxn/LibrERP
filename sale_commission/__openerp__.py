# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
#    $Id$
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
    'name': 'Sales commissions',
    'version': '1.0.e',
    'author': 'Pexego',
    "category": "Generic Modules/Sales & Purchases",
    'depends': [
        'base',
        'account',
        'product',
        'sale',
        'hr',
        'stock',
        'sale_crm'
    ],
    'description': 'Sales commissions',
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        # 'views/saleagent_view.xml',
        # 'views/partner_agent_view.xml',
        # 'wizard/wizard_invoice.xml',
        # 'views/partner_view.xml',
        # 'views/settled_view.xml',
        # 'views/invoice_view.xml',
        # 'views/sale_order_view.xml',
        # 'views/product_view.xml',
        # 'views/stock_picking_view.xml',
        # 'report/cc_commission_report.xml',
    ],

    'active': False,
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

