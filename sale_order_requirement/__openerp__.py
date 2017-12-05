{
    "name": "Sale Order Requirement",
    "version": "4.5.8.7",
    "author": "Antonio Mignolli - Didotech SRL",
    "category": 'Sales Management',
    "description": """
Create order requirements based on sale orders
===============================================

This module allows to view all the requirements for satisfying a sale order,
and choose if manufacture or buy products from suppliers.

    """,
    'website': 'www.didotech.com',
    "depends": [
        "mrp",
    ],
    'data': [
        'views/order_requirement.xml',
        'views/order_requirement_line.xml',
        'views/view_company_form.xml',
    ],
    'css': ['static/src/css/style.css'],
    'installable': True,
    'auto_install': False,
}
