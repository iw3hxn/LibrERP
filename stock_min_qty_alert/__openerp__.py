# -*- coding: utf-8 -*-
# © 2020 Didotech srl (www.didotech.com)

{
    'name': 'Stock Min Qty Alert in DDT',
    'description': """
    Module ad column Location Min Qty in tree view of the product with quantity for every Location

It also turns DDT line red if product quantity in DDT is superior to products in Source Location
    """,
    'author': "Didotech SRL",
    'version': '4.0.0.0',
    'category': 'Profiling',
    'license': 'AGPL-3',
    "depends": [
        'base',
        'product',
        'stock',
        'stock_move_extended'
    ],
    "data": [
        'views/product_view.xml',
        'views/stock_view.xml'
    ],
    "css": [],
    "demo": [],
    "active": False,
    "installable": True,
    'external_dependencies': {
        'python': []
    }
}
