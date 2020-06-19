# -*- coding: utf-8 -*-

from openerp.osv import orm


class AccountAnalyticLine(orm.Model):
    _inherit = 'account.analytic.line'

    def update_or_create_line(self, cr, uid, move, values, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        production_order_ids = False
        if not context.get('force_commit', False) and move:
            production_order_ids = move.production_order_ids
        res = False
        if not production_order_ids:
            res = super(AccountAnalyticLine, self).update_or_create_line(cr, uid, move, values, context)
        return res
