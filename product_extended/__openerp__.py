# -*- coding: utf-8 -*-
# © 2014 - 2020 Didotech srl (www.didotech.com)

{
    "name": "Product Extended",
    "version": "3.9.20.18",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    'category': 'Sales Management',
    "description": """
       Module extends functionality of the product module.
   
       Now on category there is a flag to show if it has some products inside. If no product is possible to unlink
       
       Module improves search, so product is searchable by more than one word written in any order.

       'inside script directory there are a script for update al database
    """,
    "depends": [
        'base',
        'product',
        'product_bom',
        'purchase',
        'sale'
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/product_view.xml',
        'views/product_supplierinfo_view.xml',
        'views/product_category_view.xml',
    ],
    "active": False,
    "installable": True,
    'auto_install': True
}
