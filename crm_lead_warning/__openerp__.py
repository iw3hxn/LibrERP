# -*- encoding: utf-8 -*-


{
    'name': 'Module corrects a bug in crm_lead, when creating a partner. Parameter customer is True.',
    'version': '4.0.0.0',
    'category': 'Customer Relationship Management',
    'description': """Add warning on CRM """,
    "author": "Didotech SRL",
    'website': 'https://www.didotech.com',
    'depends': [
        'crm_lead_correct',
        'warning',
    ],
    'data': [
        'views/crm_make_sale_view.xml'
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
