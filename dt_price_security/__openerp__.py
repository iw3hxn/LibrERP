# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Price Security',
    'version': '3.1.4.4',
    'description': """
    Creates a new permission to restrict the users that can modify the prices
    of the products.
    
    Asociate to each user a list of pricelist and the correspoding discounts they
    can apply to sale orders and invoices.
    
    Allow the posibility to mark products so that anyone can modify their price in
    a sale order.
    """,
    'category': 'Sales Management',
    'author': 'Sistemas ADHOC',
    'website': 'http://www.sistemasadhoc.com.ar/',
    'depends': [
        'product',
        'sale',
        'purchase',
        'res_users_helper_functions',
        'sale_order_confirm'
    ],
    'data': [
        'security/price_security_security.xml',
        'views/res_users_view.xml',
        'views/sale_view.xml',
        'views/invoice_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
