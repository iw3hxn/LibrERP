# -*- coding: utf-8 -*-
#    Copyright (C) 2011-12 Domsense s.r.l. <http://www.domsense.com>.
#    Copyright (C) 2012-15 Agile Business Group sagl <http://www.agilebg.com>
#    Copyright (C) 2013-15 LinkIt Spa <http://http://www.linkgroup.it>
#    Copyright (C) 2013-17 Associazione Odoo Italia
#                          <http://www.odoo-italia.org>
#    Copyright (C) 2017    Didotech srl <http://www.didotech.com>
#    Copyright (C) 2017    SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# [2011: domsense] First version
# [2012: agilebg] Various enhancements
# [2013: openerp-italia] Various enhancements
# [2017: odoo-italia] Electronic VAT statement
{
    "name": "Period End VAT Statement",
    "version": "7.0.4.1.0",
    'category': 'Generic Modules/Accounting',
    'license': 'AGPL-3',
    "depends": ["base",
                "account_voucher",
                "report_webkit",
                "l10n_it_vat_registries",
                ],
    "author": "Agile Business Group, "
              " Odoo Italia Associazione",
    'maintainer': 'Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>',
    "description": """(en)

Period End VAT Statement
========================

This module evaluates VAT to pay (or on credit) and generates the electronic
VAT closeout statement as VAT Authority
http://www.agenziaentrate.gov.it/wps/content/nsilib/nsi/documentazione/normativa+e+prassi/provvedimenti/2017/marzo+2017+provvedimenti/provvedimento+27+marzo+2017+liquidazioni+periodiche+iva

The 'VAT statement' object allows to specify every amount and relative account
used by the statement.
By default, amounts of debit and credit taxes are automatically loaded
from tax codes of selected periods.

Previous debit or credit is loaded from previous VAT statement, according
to its payments status.

https://www.zeroincombenze.it/liquidazione-iva-elettronica-ip17


(it)

Liquidazione IVA periodica
==========================

Questo modulo calcola l'IVA da pagare (o a credito) sia per i contribuenti
mensili che trimestrali e permette di generare il file della comunicazione
elettronica come da normativa del 2017 dell'Agenzia delle Entrate
http://www.agenziaentrate.gov.it/wps/content/nsilib/nsi/documentazione/normativa+e+prassi/provvedimenti/2017/marzo+2017+provvedimenti/provvedimento+27+marzo+2017+liquidazioni+periodiche+iva

La liquidazione è calcolata sommando i totali di periodo dei conti imposte.

L'utente può aggiungere l'eventuale credito/debito del periodo precedente e
calcolare gli interessi; può anche registrare l'utilizzo del credito in
compensazione.


https://www.zeroincombenze.it/liquidazione-iva-elettronica-ip17
""",
    'website': 'https://odoo-italia.org',
    'data': [
        'wizard/add_period.xml',
        'wizard/remove_period.xml',
#        'wizard/vat_settlement.xml',
        'statement_workflow.xml',
        'security/ir.model.access.csv',
        'reports.xml',
        'views/account_view.xml',
        'views/company_view.xml',
    ],
    'external_dependencies': {
        'python': ['pyxb'],
    },
    'demo': [],
    'installable': True,
}
