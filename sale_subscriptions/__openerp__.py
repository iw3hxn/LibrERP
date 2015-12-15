# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012-2015 Didotech (<http://www.didotech.com>).
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
    "name": "Subscrption Sale",
    "version": "3.3.17.11",
    "author": "Agile Business Group & Domsense & Didotech",
    'website': 'http://www.didotech.com',
    'category': 'Generic Modules/Sales & Purchases',
    "description": """This module allows to sale subscription products and generate new quotations when subscription ends.
    
    For more info: http://planet.domsense.com/en/2011/06/selling-subscriptions-with-openerp/
    """,
    'depends': [
        "sale",
        'sale_margin',
        'core_extended'
        # "sale_layout",
        # "tko_sale_validation",
    ],
    'data': [
        "security/ir.model.access.csv",
        'product_view.xml',
        'views/sale_view.xml',
        'views/sale_order_menu.xml',
        'orders_renew.xml',
        'cron.xml',
        'company_view.xml'
    ],
    'installable': True,
    'active': False,
}
