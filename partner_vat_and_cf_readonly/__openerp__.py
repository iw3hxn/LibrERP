# -*- coding: utf-8 -*-

{
    'name': 'Partner Vat and Fiscal Code readonly',
    'version': "3.0.0.0",
    'author': "Didotech SRL",
    'website': "http://www.didotech.com",
    'category': 'Partner',
    'description': """
     This module changes attribute of vat field and fiscal code field 'readonly' to false after an amount of minutes specified in system params with key 'vatcf_minutes_amount_readonly'
    """,
    'license': 'AGPL-3',
    "depends": [
        'base',
        'account',
        'partner_subaccount',
        'l10n_it_account'
    ],
    "data": [
        'views/vat_cf_view.xml',
        'data/vat_amount_of_minutes_data.xml'
    ],
    "demo": [],
    "active": False,
    "installable": True,
    "application": True,
}

