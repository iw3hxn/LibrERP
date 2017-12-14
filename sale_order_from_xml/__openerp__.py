# -*- coding: utf-8 -*-
# © 2014 - 2017 Didotech srl (www.didotech.com)

{
    "name": "Order from XML",
    "version": "4.0.0.0",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    'category': 'Sales Management',
    "description": """
       Module permits to create orders from XML
    """,
    "depends": [
        'base',
        'product',
        'sale'
    ],
    "data": [],
    "active": False,
    "installable": True,
    'auto_install': True,
    'external_dependencies': {
        'python': [
            'xmltodict',
        ]
    }
}
