# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

{
    "name": "Attendance Position",
    "version": "4.1.1.2",
    "author": "Andrei Levin - Didotech SRL",
    "category": 'Partner',
    "description": """
Get geographic position of a partner address from Google Maps
=============================================================

    """,
    'website': 'www.didotech.com',
    "depends": [
        "base",
        'base_address_contacts',
        "hr_attendance"
    ],
    'data': [
        # 'security/ir_model_access.csv',
        'views/data.xml',
        'views/company_view.xml',
        'views/partner_view.xml',
        'views/hr_attendance.xml',
        'wizard/set_coordinates.xml'
    ],
    'installable': True,
    'auto_install': False,
    "external_dependencies": {
        "python": [
            'googlemaps'
        ],
        "bin": []
    }
}
