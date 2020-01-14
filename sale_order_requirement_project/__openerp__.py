{
    "name": "Sale Order Requirement Project",
    "version": "4.2.3.1",
    "author": "Didotech SRL",
    "category": 'Sales Management',
    "description": """
    
Create order requirements based on sale orders
===============================================

This module extend Sale Order Requirement for task (service product)

* Remember that must be deactive task creation of Work Order


    """,
    'website': 'www.didotech.com',
    "depends": [
        'sale_order_requirement',
        'project',
        'work_order'
    ],
    'data': [
        'data/company_data.xml',
        'views/order_requirement.xml',
        'views/order_requirement_line.xml',
        'views/product_view.xml',
        'views/menu.xml'
    ],
    'installable': True,
    'auto_install': False,
}
