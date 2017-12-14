# -*- coding: utf-8 -*-
# © 2014 - 2017 Didotech srl (www.didotech.com)

{
    "name": "Order from XML",
    "version": "4.1.1.1",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    'category': 'Sales Management',
    "description": """
       Module permits to create orders from XML
       
       Path to XML files should be set inside Company -> Configuration
       
       If 'Confirm automatically imported orders' (inside Company -> Configuration) is set to True, 
       imported orders will be automatically confirmed after import
    """,
    "depends": [
        'base',
        'product',
        'sale'
    ],
    "data": [
        'cron.xml',
        'views/company_view.xml'
    ],
    "active": False,
    "installable": True,
    'auto_install': True,
    'external_dependencies': {
        'python': [
            'xmltodict',
        ]
    }
}
