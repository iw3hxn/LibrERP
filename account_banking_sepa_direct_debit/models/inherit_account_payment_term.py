# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class account_payment_term(orm.Model):
    # flag riba utile a distinguere la modalità di pagamento
    _inherit = 'account.payment.term'

    _columns = {
        'sdd': fields.boolean('SDD'),
    }

    _defaults = {
        'sdd': False,
    }
