{
    "name": "Sale Order Requirement",
    "version": "4.39.62.59",
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
        "stock_picking_extended",
        "purchase",
        "work_order",
        "res_users_helper_functions",
    ],
    'data': [
        'wizard/order_requirement_line_add.xml',
        'views/order_requirement.xml',
        'views/order_requirement_line.xml',
        'views/view_company_form.xml',
        'views/mrp_view.xml',
        'views/mrp_production_view.xml',
        'views/purchase_view.xml',
        'views/stock_picking.xml',
        'security/ir.model.access.csv',
        'views/sale_workflow.xml',
        'views/sale_order_view.xml',
        'report/order_requirement.xml',
        'report/stock_picking_in_report.xml'
 #       'report/incoming_bill.xml',
    ],
    'css': ['static/src/css/style.css'],
    'installable': True,
    'auto_install': False,
}
