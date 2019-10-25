# -*- coding: utf-8 -*-
# © 2019 - Giovanni Monteverde - Didotech srl
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
{
    'name': 'Report Electronic Invoice Import',
    'version': '3.0.2.1',
    'category': 'Localization/Italy',
    'description': """
        Sent a Email with a list of new imported Electronic Invoices
    """,
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'base',
        'account'
    ],
    "data": [
        'data/cron.xml'
    ],
    "demo": [],
    "active": False,
    "installable": True,
    "application": True,
}
