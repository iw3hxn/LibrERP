# -*- coding: utf-8 -*-
# © 2015-2017 Didotech srl (www.didotech.com)

{
    'name': 'Data migration import',
    'version': '3.12.81.21',
    'category': 'Tools',
    'description': """
        This module gives a possibilitie to import products and partners
        from CSV/Excel/OpenOffice formatted files.

        When option 'strict' is selected, partner will be searched on every
        field in PARTNER_SEARCH and if in doubt nothing will be changed or
        updated. It is usefull to use this mode to be shure that nothing will
        be overwritten.
    """,
    "author": "Didotech SRL",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'purchase',
        # 'partner_subaccount',
        # 'l10n_it', not needed, pdc is installed
        # 'l10n_it_account',
        'core_extended',
        'email_message_custom'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/file_import_view.xml',
        'wizard/sale_order_state_view.xml',
        'partner_template_view.xml'
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [
            'xlrd',
        ]
    }
}
