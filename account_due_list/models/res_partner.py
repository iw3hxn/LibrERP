# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2018 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time


from openerp.osv import fields, orm
from tools import DEFAULT_SERVER_DATE_FORMAT


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _get_account_to_view(self, cr, uid, partner, context):
        account_view_ids = []
        account_view_partner_ids = []
        if context.get('search_default_supplier', False):
            account_view_partner_ids.append(partner.property_account_payable.id)
        if context.get('search_default_customer', False):
            account_view_partner_ids.append(partner.property_account_receivable.id)

        if not account_view_ids:
            account_view_partner_ids.append(partner.property_account_payable.id)
            account_view_partner_ids.append(partner.property_account_receivable.id)

        fposition_id = partner.property_account_position
        if fposition_id:
            for account_id in account_view_partner_ids:
                account_view_ids.append(
                    self.pool['account.fiscal.position'].map_account(cr, uid, fposition_id, account_id,
                                                                     context=context))
        account_view_ids += account_view_partner_ids
        account_view_ids = list(set(account_view_ids))
        return account_view_ids

    def _get_invoice_payment(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner_id in ids:
            res[partner_id] = []

        for partner in self.browse(cr, uid, ids, context):
            account_view_ids = self._get_account_to_view(cr, uid, partner, context)
            res[partner.id] = self.pool['account.move.line'].search(cr, uid, [('account_id', 'in', account_view_ids), ('partner_id', '=', partner.id), ('reconcile_id', '=', False)], context=context)
        return res

    def _get_credit_activity_history_last(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, False)

        cr.execute("""SELECT DISTINCT
                            credit_phonecall.partner_id,
                            MAX(credit_phonecall.date)
                        FROM
                            credit_phonecall
                        WHERE
                            credit_phonecall.state = 'done' AND
                            credit_phonecall.partner_id in %s
                        GROUP BY
                            credit_phonecall.partner_id
                        """, (tuple(ids),))
        res_sql = cr.fetchall()
        for res_id in res_sql:
            res[res_id[0]] = res_id[1]

        return res

    def _get_credit_activity_history_next(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, False)

        cr.execute("""SELECT DISTINCT
                            credit_phonecall.partner_id,
                            MIN(credit_phonecall.date)
                        FROM
                            credit_phonecall
                        WHERE
                            credit_phonecall.state in ('draft', 'open', 'pending') AND
                            credit_phonecall.partner_id in %s
                        GROUP BY
                            credit_phonecall.partner_id
                        """, (tuple(ids),))
        res_sql = cr.fetchall()
        for res_id in res_sql:
            res[res_id[0]] = res_id[1]

        return res

    def _search_next_overdue_credit_activity_date(self, cr, uid, obj, name, args, context=None):
        if args:
            current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            cr.execute("""SELECT 
                    credit_phonecall.partner_id
                FROM 
                    credit_phonecall
                WHERE 
                    credit_phonecall.state in ('draft', 'open', 'pending') AND 
                    credit_phonecall.date <= %s 
                GROUP BY
                    partner_id;
            """, (current_date + ' 23:59:59', ))

            res = cr.fetchall()
            partner_ids = []
            if res:
                partner_ids = [x[0] for x in res]

            if not partner_ids:
                return [('id', '=', 0)]
            return [('id', 'in', list(set(partner_ids)))]

        return []

    def _get_overdue_credit(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        cr.execute("""SELECT
                            account_move_line.partner_id,
                            SUM(account_move_line.debit) - SUM(account_move_line.credit)
                        FROM
                            account_account,
                            account_move_line
                        WHERE
                            account_move_line.account_id = account_account.id AND
                            account_move_line.state != 'draft' AND
                            account_account.type = 'receivable' AND
                            account_move_line.reconcile_id IS NULL AND
                            partner_id in %s AND
                            (account_move_line.date_maturity <= %s 
                                OR
                            account_move_line.date <= %s AND account_move_line.date_maturity IS NULL)
                            
                        GROUP BY
                            partner_id;
                    """, (tuple(ids), current_date, current_date))
        res_sql = cr.fetchall()
        for res_id in res_sql:
            res[res_id[0]] = res_id[1]
        return res

    def _get_overdue_debit_positive(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        cr.execute("""SELECT
                                account_move_line.partner_id,
                                COALESCE(SUM(account_move_line.debit) - SUM(account_move_line.credit), 0) AS amount
                            FROM
                                account_account,
                                account_move_line
                            WHERE
                                account_move_line.account_id = account_account.id AND
                                account_move_line.state != 'draft' AND
                                account_account.type = 'receivable' AND
                                account_move_line.reconcile_id IS NULL AND
                                partner_id in %s AND
                                (account_move_line.date_maturity <= %s 
                                    OR
                                account_move_line.date <= %s AND account_move_line.date_maturity IS NULL)
                            GROUP BY
                                partner_id
                      
                    """, (tuple(ids), current_date, current_date))
        res_sql = cr.fetchall()
        for res_id in res_sql:
            if res_id[1] >= 0:
                res[res_id[0]] = True
            else:
                res[res_id[0]] = False
        return res

    def _search_overdue_credit(self, cr, uid, obj, name, args, context=None):
        if args:
            current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            cr.execute("""
            SELECT 
                    account_move_line.partner_id
                FROM 
                    account_account, 
                    account_move_line,
                    res_partner
                WHERE 
                    account_move_line.account_id = account_account.id AND
                    account_move_line.partner_id = res_partner.id AND
                    (res_partner.collections_out != 'True' OR res_partner.collections_out IS NULL) AND
                    account_move_line.state != 'draft' AND 
                    account_account.type = 'receivable' AND 
                    account_move_line.reconcile_id IS NULL AND
                    account_move_line.date_maturity <= %s
                GROUP BY
                    partner_id
            """, (current_date, ))

            res = cr.fetchall()
            partner_ids = []
            if res:
                partner_ids = [x[0] for x in res]

            if not partner_ids:
                return [('id', '=', 0)]
            return [('id', 'in', list(set(partner_ids)))]

        return []


    def _search_overdue_debit_positive(self, cr, uid, obj, name, args, context=None):
        if args:
            current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            cr.execute("""
            SELECT
                account_move_line.partner_id,
                COALESCE(SUM(account_move_line.debit) - SUM(account_move_line.credit), 0) AS amount
            FROM
                account_account,
                account_move_line
            WHERE
                account_move_line.account_id = account_account.id AND
                account_move_line.state != 'draft' AND
                account_account.type = 'receivable' AND
                account_move_line.reconcile_id IS NULL AND
                partner_id in (
                    SELECT 
                                account_move_line.partner_id
                            FROM 
                                account_account, 
                                account_move_line,
                                res_partner
                            WHERE 
                                account_move_line.account_id = account_account.id AND
                                account_move_line.partner_id = res_partner.id AND
                                (res_partner.collections_out != 'True' OR res_partner.collections_out IS NULL) AND
                                account_move_line.state != 'draft' AND 
                                account_account.type = 'receivable' AND 
                                account_move_line.reconcile_id IS NULL AND
                                account_move_line.date_maturity <= %s
                            GROUP BY
                                partner_id )
                AND
                    (account_move_line.date_maturity <= %s 
                        OR
                    account_move_line.date <= %s AND account_move_line.date_maturity IS NULL)
                GROUP BY
                    partner_id
            """, (current_date, current_date, current_date, ))

            res = cr.fetchall()
            partner_ids = []
            if res:
                for rec in res:
                    if rec[1] >= 0:
                        partner_ids.append(rec[0])

            if not partner_ids:
                return [('id', '=', 0)]
            return [('id', 'in', list(set(partner_ids)))]

        return []

    _columns = {
        'payment_ids': fields.function(_get_invoice_payment, string="All Open Payment", type='one2many',
                                       method=True, relation='account.move.line'),
        'overdue_credit': fields.function(_get_overdue_credit, fnct_search=_search_overdue_credit, string="Overdue Payment", type='float', method=True),
        'overdue_debit_positive': fields.function(_get_overdue_debit_positive, fnct_search=_search_overdue_debit_positive, string="Overdue positive", type='boolean', method=True),
        'last_overdue_credit_activity_date': fields.function(_get_credit_activity_history_last, method=True, string="Last Activity On", type='date'),
        'next_overdue_credit_activity_date': fields.function(_get_credit_activity_history_next, fnct_search=_search_next_overdue_credit_activity_date, method=True, string="Next Activity On", type='date'),
        'collections_out': fields.boolean('Recupero Presso Terzi'),
        'credit_phonecall_ids': fields.one2many('credit.phonecall', 'partner_id', 'Phonecalls'),
        'excluding_recall': fields.boolean('Escluso dai richiami'),
    }

