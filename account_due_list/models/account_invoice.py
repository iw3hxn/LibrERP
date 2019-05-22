##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved


from openerp.osv import fields, orm


class account_invoice(orm.Model):

    _inherit = 'account.invoice'

    _columns = {
        'to_pay': fields.boolean('To Pay', readonly=True, help="This field will be marked when the purchase manager approve this invoice to be paid, and unmarked if the invoice will be blocked to pay"),
    }
    _defaults = {
        'to_pay': True,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'to_pay': True,
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)

    def payment_approve(self, cr, uid, ids, context=None):
        '''
        Mark boolean as True, to approve invoice to be pay.
        Added message to messaging block of supplier invoice,
        when approve invoice.
        '''
        context = context or self.pool['res.users'].context_get(cr, uid)
        self._update_blocked_payment(cr, uid, ids, False, context)

        return self.write(cr, uid, ids, {'to_pay': True}, context)

    def payment_disapproves(self, cr, uid, ids, context=None):
        '''
        Mark boolean as False, to Disapprove invoice to be pay.
        Added message to messaging block of supplier invoice,
        when disapproved to Pay.
        '''
        context = context or self.pool['res.users'].context_get(cr, uid)
        self._update_blocked_payment(cr, uid, ids, True, context)

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
        return account_move_line.write(cr, uid, move_line_ids, {'blocked': block}, context=context)
