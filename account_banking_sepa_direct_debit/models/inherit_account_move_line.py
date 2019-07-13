# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def _get_fields_sdd_function(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = dict.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids, context):
            if line.stored_invoice_id:
                if line.stored_invoice_id.payment_term:
                    res[line.id] = line.stored_invoice_id.payment_term.sdd
        return res

    def _set_sdd(self, cr, uid, ids, name, value, arg, context=None):
        if not name:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]

        cr.execute("""update account_move_line set
                    sdd=%s where id in (%s)""", (value, ', '.join([str(line_id) for line_id in ids])))
        return True

    def _get_sdd_from_account_invoice(self, cr, uid, ids, context=None):
        invoice_pool = self.pool['account.invoice']
        res = []
        for invoice in invoice_pool.browse(cr, uid, ids, context=context):
            if invoice.move_id:
                for line in invoice.move_id.line_id:
                    if line.id not in res:
                        res.append(line.id)
        return res

    def _get_sdd_from_payment_term(self, cr, uid, ids, context=None):
        account_invoice_ids = self.pool['account.invoice'].search(cr, uid, [('payment_term', 'in', ids)], context=context)
        return self.pool['account.move.line'].search(cr, uid, [('stored_invoice_id', 'in', account_invoice_ids)], context=context)

    _columns = {
        'sdd': fields.function(_get_fields_sdd_function, type='boolean', string='SDD', fnct_inv=_set_sdd, store={
            'account.move.line': (lambda self, cr, uid, ids, c={}: ids, ['stored_invoice_id'], 7000),
            'account.invoice': (_get_sdd_from_account_invoice, ['payment_term', 'move_id'], 7000),
            'account.payment.term': (_get_sdd_from_payment_term, ['sdd'], 7000),
        }),
    }

