# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Didotech SRL (<http://didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import decimal_precision as dp


class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'

    def _debit_credit_bal_qtty(self, cr, uid, ids, fields, arg, context=None):
        super(account_analytic_account, self)._debit_credit_bal_qtty(cr, uid, ids, fields, arg, context)
        res = {}
        if context is None:
            context = {}
        child_ids = tuple(self.search(cr, uid, [('parent_id', 'child_of', ids)]))
        for i in child_ids:
            res[i] = {}
            for n in fields:
                res[i][n] = 0.0

        if not child_ids:
            return res

        where_date = ''
        where_clause_args = [tuple(child_ids)]
        if context.get('from_date', False):
            where_date += " AND l.date >= %s"
            where_clause_args += [context['from_date']]
        if context.get('to_date', False):
            where_date += " AND l.date <= %s"
            where_clause_args += [context['to_date']]
        cr.execute("""
              SELECT a.id,
                     sum(
                         CASE WHEN l.amount > 0
                         THEN l.amount
                         ELSE 0.0
                         END
                          ) as credit,
                     sum(
                         CASE WHEN l.amount < 0
                         THEN -l.amount
                         ELSE 0.0
                         END
                          ) as debit,
                     COALESCE(SUM(l.amount),0) AS balance,
                     COALESCE(SUM(l.unit_amount),0) AS quantity
              FROM account_analytic_account a
                  LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
              WHERE a.id IN %s
              """ + where_date + """
              GROUP BY a.id""", where_clause_args)
        for row in cr.dictfetchall():
            res[row['id']] = {}
            for field in fields:
                res[row['id']][field] = row[field]
        return super(account_analytic_account, self)._compute_level_tree(cr, uid, ids, child_ids, res, fields, context)

    _columns = {
        'debit': fields.function(_debit_credit_bal_qtty, type='float', string='Debit', multi='debit_credit_bal_qtty', digits_compute=dp.get_precision('Account')),
        'credit': fields.function(_debit_credit_bal_qtty, type='float', string='Credit', multi='debit_credit_bal_qtty', digits_compute=dp.get_precision('Account')),
    }

account_analytic_account()


class account_analytic_line(osv.osv):
    _inherit = 'account.analytic.line'

    _columns = {
        'partner_id': fields.related('move_id', 'partner_id', type="many2one", relation="res.partner", string="Partner"),
        'supplier_invoice_id': fields.related('move_id', 'invoice', 'supplier_invoice_number', type="char", relation="account.invoice", string="Supplier Invoice"),
        'invoice_id': fields.related('move_id', 'invoice', 'number', type="char", relation="account.invoice", string="Invoice"),
    }

account_analytic_line()
