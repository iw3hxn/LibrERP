# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

{
    'name': 'CRM Sales Team Region',
    'version': '4.2.1.4',
    "author": "Didotech Srl",
    "website": "www.didotech.com",
    'category': 'Customer Relationship Management',
    "description": """
Sales Team Region
=================

Module addes possibility to assign a region to a Sales Team and automatically assign Sales Team to a client based on his/her address
    """,
    'license': 'AGPL-3',
    "depends": [
        'crm',
        'l10n_it_base',
        'base_address_contacts'
    ],
    "data": [
        'security/security.xml',
        'views/crm_view.xml',
        'views/res_partner.xml',
        'views/region_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True,
    'external_dependencies': {
        'python': []
    }
}
