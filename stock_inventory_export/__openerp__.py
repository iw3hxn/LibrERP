# -*- encoding: utf-8 -*-

{
    'name': 'Export Inventory Costs',
    'version': '3.0.0.0',
    'category': "Warehouse Management",
    'description': """
        Export Inventory Costs
    """,
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'base',
        'stock',
    ],
    "data": [
        'wizard/wizard_inventory_costs_view.xml',
        'views/stock_view.xml'
    ],
    "demo": [],
    "active": False,
    "installable": True,
    "application": True,
}
