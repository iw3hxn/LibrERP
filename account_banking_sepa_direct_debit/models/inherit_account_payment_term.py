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


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    _columns = {
        'distinta_line_ids': fields.one2many('riba.distinta.move.line', 'move_line_id', "Dettaglio riba"),
        'riba': fields.related('stored_invoice_id', 'payment_term', 'riba',
            type='boolean', string='RiBa', store=False),
        'unsolved_invoice_ids': fields.many2many('account.invoice', 'invoice_unsolved_line_rel', 'line_id', 'invoice_id', 'Unsolved Invoices'),
        'iban': fields.related('partner_id', 'bank_ids', 'iban', type='char', string='IBAN', store=False),
        'abi': fields.related('partner_id', 'bank_riba_id', 'abi', type='char', string='ABI', store=False),
        'cab': fields.related('partner_id', 'bank_riba_id', 'cab', type='char', string='CAB', store=False),
    }
    _defaults = {
        'distinta_line_ids': None,
    }

