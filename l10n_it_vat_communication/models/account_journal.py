# -*- coding: utf-8 -*-
# Copyright 2017 - Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
#                  Associazione Odoo Italia <http://www.odoo-italia.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import orm, fields
# from l10n_it_ade.ade import ADE_LEGALS


class account_journal(orm.Model):
    _inherit = "account.journal"

    _columns = {
        'rev_charge': fields.boolean(
            'Reverse Charge Journal',
            help="Check if reverse charge EU invoices journal"),
    }

    _defaults = {
        'rev_charge': False,
    }
