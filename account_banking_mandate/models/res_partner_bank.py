# -*- coding: utf-8 -*-
# Copyright 2014, Compassion CH (http://www.compassion.ch)
# Copyright 2017, Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
# Copyright 2017, Associazione Odoo Italia <https://odoo-italia.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import fields, orm
from openerp.tools.translate import _


class ResPartnerBank(orm.Model):
    _inherit = 'res.partner.bank'

    _columns = {
        'mandate_ids': fields.one2many(
            'account.banking.mandate', 'partner_bank_id',
            _('Banking Mandates'),
            help=_('Banking mandates represents an authorization that the '
                   'bank account owner gives to a company for a specific '
                   'operation')),
    }
