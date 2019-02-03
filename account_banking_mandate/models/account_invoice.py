# -*- coding: utf-8 -*-
# Copyright 2014, Compassion CH (http://www.compassion.ch)
# Copyright 2017, Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
# Copyright 2017, Associazione Odoo Italia <https://odoo-italia.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import fields, orm


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'mandate_id': fields.many2one(
            'account.banking.mandate', 'Direct Debit Mandate',
            domain=[('state', '=', 'valid')], readonly=True,
            states={'draft': [('readonly', False)]})
    }
