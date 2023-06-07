##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved

from tools.translate import _
from openerp.osv import fields, orm


class AccountInvoice(orm.Model):

    _inherit = 'account.invoice'

    def _get_len_credit_phonecall_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        cr.execute("""
            SELECT invoice_id, COUNT(*) AS call_count
            FROM credit_phonecall
            WHERE invoice_id in %s
            GROUP BY invoice_id;
        """, (tuple(ids),))
        res_sql = cr.fetchall()
        for res_id in res_sql:
            res[res_id[0]] = res_id[1]
        return res

    def _compute_payment_delta_days(self, cr, uid, ids, field_names, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            payment_delta = 0
            payment_delta_days = []
            for payment_line in invoice.maturity_ids:
                payment_delta_days.append(payment_line.payment_delta_days)
            payment_delta = sum(payment_delta_days) / len(payment_delta_days) if len(payment_delta_days) else 0
            res[invoice.id] = payment_delta
        return res

    _columns = {
        'to_pay': fields.boolean(
            string='To Pay',
            readonly=True,
            help="This field will be marked when the purchase manager approve this invoice to be paid, and unmarked if the invoice will be blocked to pay"
        ),
        'credit_phonecall_ids': fields.one2many('credit.phonecall', 'invoice_id', 'Phonecalls'),
        'len_credit_phonecall_ids': fields.function(_get_len_credit_phonecall_ids, string="Numero Solleciti",
                                                    type='integer', method=True),
        'payment_delta_days': fields.function(
            _compute_payment_delta_days,
            type="integer",
            string="Payment Delta Day",
            method=True
        ),
    }
    _defaults = {
        'to_pay': True,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'to_pay': True,
        })
        return super(AccountInvoice, self).copy(cr, uid, id, default, context)

    def payment_approve(self, cr, uid, ids, context=None):
        '''
        Mark boolean as True, to approve invoice to be pay.
        Added message to messaging block of supplier invoice,
        when approve invoice.
        '''
        context = context or self.pool['res.users'].context_get(cr, uid)
        self._update_blocked_payment(cr, uid, ids, False, context)
        text = _("Approve payment")
        self.message_append(cr, uid, ids, text, body_text=text, context=context)
        return self.write(cr, uid, ids, {'to_pay': True}, context)

    def payment_disapproves(self, cr, uid, ids, context=None):
        '''
        Mark boolean as False, to Disapprove invoice to be pay.
        Added message to messaging block of supplier invoice,
        when disapproved to Pay.
        '''
        context = context or self.pool['res.users'].context_get(cr, uid)
        self._update_blocked_payment(cr, uid, ids, True, context)
        text = _("Block payment")
        self.message_append(cr, uid, ids, text, body_text=text, context=context)
        return self.write(cr, uid, ids, {'to_pay': False}, context=context)

    def _update_blocked_payment(self, cr, uid, ids, block, context):
        account_move_line = self.pool['account.move.line']
        move_line_ids = []
        for invoice in self.browse(cr, uid, ids, context):
            partner_id = invoice.partner_id.id
            account_id = invoice.account_id.id
            move_id = invoice.move_id and invoice.move_id.id
            move_line_ids += account_move_line.search(cr, uid,
                                                      [('account_id', '=', account_id), ('partner_id', '=', partner_id),
                                                       ('move_id', '=', move_id)], context=context)
        return account_move_line.write(cr, uid, list(set(move_line_ids)), {'blocked': block}, context=context)
