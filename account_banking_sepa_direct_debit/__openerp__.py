# -*- coding: utf-8 -*-
#    Copyright (C) 2019 Didotech SRL

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Banking SEPA Direct Debit',
    'summary': 'Create SEPA files for Direct Debit',
    'version': '6.0.4.8.2',
    'license': 'AGPL-3',
    'author': "Didotech SRL",
    'website': 'http://www.akretion.com',
    'category': 'Banking addons',
    'depends': [
        'account_banking_mandate',
        'l10n_it_ricevute_bancarie',
    ],
    'external_dependencies': {
        'python': ['unidecode', 'lxml'],
    },
    'data': [
        'views/account_view.xml',
        'views/riba_configurazione.xml',
        'views/riba_distinta.xml'
    ],

    'description': '''
Module to export direct debit payment orders in SEPA XML file format.

    ''',
    'installable': True,
}
