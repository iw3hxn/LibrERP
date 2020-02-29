# -*- coding: utf-8 -*-
#    Copyright (C) 2017    SHS-AV s.r.l. <https://www.zeroincombenze.it>
#    Copyright (C) 2017-2020    Didotech srl <http://www.didotech.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# [2017: SHS-AV s.r.l.] First version

{
    "name": "Comunicazione periodica IVA",
    "version": "6.1.0.6.13",
    'category': 'Generic Modules/Accounting',
    'license': 'AGPL-3',
    "depends": [
        "l10n_it_ade",
        "account_invoice_entry_date",
        "l10n_it_vat_registries",
        'l10n_it_account'
    ],
    "author":  "SHS-AV s.r.l.,"
               " Odoo Italia Associazione",
    'maintainer': 'Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>',
    "description": """(en)

Period VAT communication
========================

This module generate the xml file for sending to Agenzia delle Entrate
http://www.agenziaentrate.gov.it/wps/content/Nsilib/Nsi/Strumenti/Specifiche+tecniche/Specifiche+tecniche+comunicazioni/Fatture+e+corrispettivi+ST/



(it)

Comunicazione IVA periodica
===========================

Questo modulo genera in file XML da inviare all'Agenzia delle Entrate
http://www.agenziaentrate.gov.it/wps/content/Nsilib/Nsi/Strumenti/Specifiche+tecniche/Specifiche+tecniche+comunicazioni/Fatture+e+corrispettivi+ST/

Questa comunicazione è anche conosciuta come Spesometro light 2018.
""",
    'website': 'https://odoo-italia.org',
    'data': [
        'views/add_period.xml',
        'views/remove_period.xml',
        'views/account_view.xml',
        'views/wizard_export_view.xml',
        'security/ir.model.access.csv',
        'communication_workflow.xml',
    ],
    'external_dependencies': {
        'python': ['pyxb', 'unidecode'],
    },
    'demo': [],
    'installable': True,
}
