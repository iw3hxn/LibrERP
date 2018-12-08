# -*- encoding: utf-8 -*-

{
    'name': 'Product Pricelist Extended',
    'version': "3.0.0.1",
    'author': "Didotech SRL",
    'website': "http://www.didotech.com",
    'category': 'Sales Management',
    'description': """
    Extend Pricelist

    """,
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'product',
        'dt_product_pricelist_fixed_price',
    ],
    "data": [
        'views/product_product_view.xml',
        'views/product_pricelist_view.xml',
        'views/product_pricelist_item_view.xml',
        'views/product_pricelist_version_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True,
    "application": True,
}
