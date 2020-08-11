# -*- encoding: utf-8 -*-

{
    'name': 'Product Pricelist Extended',
    'version': "3.3.2.3",
    'author': "Didotech SRL",
    'website': "http://www.didotech.com",
    'category': 'Sales Management',
    'description': """
    Extend Pricelist

    """,
    'license': 'AGPL-3',
    "depends": [
        'product',
        'sale',
        'dt_product_pricelist_fixed_price',
        'res_users_helper_functions'
    ],
    "data": [
        'security/product_pricelist_security.xml',
        'views/product_product_view.xml',
        'views/product_pricelist_view.xml',
        'views/product_pricelist_item_view.xml',
        'views/product_pricelist_version_view.xml',
        'wizard/wizard_product_pricelist_item_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True,
    "application": True,
}
