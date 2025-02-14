# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012 Pexego Sistemas Informáticos (<http://tiny.be>).
#    Copyright (C) 2020 Didotech S.r.l. (<http://www.didotech.com/>).
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
    "name": "Purchase Order Lines With Discounts",
    "author": "Tiny, Pexego",
    "version": "1.3.5",
    "category": "Generic Modules/Sales & Purchases",
    'description': """ """,
    "depends": [
        "stock",
        'product',
        "purchase",
        "product_visible_discount"
    ],
    "data": [
        "views/purchase_discount_view.xml",
        'views/product_view.xml'
    ],
    "active": False,
    "installable": True
}
