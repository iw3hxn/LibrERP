# -*- coding: utf-8 -*-
# © 2018 Antonio Mignolli - Didotech srl (www.didotech.com)

{
    'name': 'Account Bank Statement Import',
    'version': '3.0.0.0',
    'category': 'Localisation',
    'description': """This module let to import account bank statements

""",
    'author': 'Antonio Mignolli - Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'account',
    ],
    "data": [
        # 'security/security.xml',
        'views/account_bank_statement_import_template_view.xml',
        'wizards/account_bank_statement_import_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
