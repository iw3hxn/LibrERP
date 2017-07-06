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
    "version": "7.0.2.1.6",
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
    "description": """

This module helps to register the VAT statement of period end.
    
In order to load correct amount from tax code, the tax code has to be associated to account involved in statement, through tax code form.

In order to load correct amount from tax code, the tax code has to be
associated to account involved in statement, through tax code form.

The 'VAT statement' object allows to specify every amount and relative account
used by the statement.
By default, amounts of debit and credit taxes are automatically loaded
from tax codes of selected periods.
Previous debit or credit is loaded from previous VAT statement, according
to its payments status.
Confirming the statement, the 'account.move' is created. If you select
a payment term, the due date(s) will be set.

The 'tax authority' tab contains information about payment(s).
You can see statement's result ('authority VAT amount') and residual
amount to pay ('Balance').
The statement can be paid like every other debit: by voucher or 'move.line'
reconciliation.

Specification:
https://www.zeroincombenze.it/liquidazione-iva-elettronica-ip17/
""",
    'website': 'http://www.didotech.com',
    'data': ['wizard/add_period.xml',
             'wizard/remove_period.xml',
             'views/account_view.xml',
             'views/company_view.xml',
             'statement_workflow.xml',
             'security/ir.model.access.csv',
             'reports.xml', ],
    'demo': [],
    'installable': True,
    'active': False,
}
