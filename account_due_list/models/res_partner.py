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

import locale
import logging

import time

from openerp.osv import fields, orm
from tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

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

    def _get_len_credit_phonecall_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        cr.execute("""
            SELECT partner_id, COUNT(*) AS call_count
            FROM credit_phonecall
            GROUP BY partner_id;
        """)
        res_sql = cr.fetchall()
        for res_id in res_sql:
            res[res_id[0]] = res_id[1]
        return res
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

    def _compute_payment_prospect(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = dict.fromkeys(ids, "")
        if ids:
            cr.execute(query="""
                SELECT
                    partner_id,
                    EXTRACT(YEAR FROM date_invoice) AS year,
                    COUNT(id) AS num_invoice,
                    COUNT(CASE WHEN state = 'open' THEN id END) AS num_invoice_open,
                    COUNT(CASE WHEN state = 'paid' THEN id END) AS num_invoice_paid,
                    SUM(CASE WHEN state = 'open' THEN amount_total ELSE 0 END) AS open,
                    SUM(CASE WHEN state = 'paid' THEN amount_total ELSE 0 END) AS paid
                FROM
                    account_invoice
                WHERE
                    type = 'out_invoice'
                    AND partner_id IN %s
                    AND state IN ('open', 'paid')
                GROUP BY
                    partner_id,
                    EXTRACT(YEAR FROM date_invoice)
            """, params=(tuple(ids),))
            res_sql = cr.fetchall()
        else:
            res_sql = []
        partner_dict = {}

        for row in res_sql:
            partner_id = row[0]
            year = int(row[1]) if row[1] else 0
            num_invoice = row[2]
            num_invoice_open = row[3]
            num_invoice_paid = row[4]
            open = row[5]
            paid = row[6]

            # Verifica se il partner_id esiste già nel dizionario
            if partner_id not in partner_dict:
                partner_dict[partner_id] = {}

            # Aggiungi i dati dell'anno al dizionario del partner_id
            partner_dict[partner_id][year] = {
                'num_invoice': num_invoice,
                'open': open,
                'paid': paid,
                'num_invoice_open': num_invoice_open,
                'num_invoice_paid': num_invoice_paid,
            }

        for _id in ids:
            if not partner_dict:
                res[_id] = "No Fatture"
                continue

            html_table = """
                        <table class="table">
                            <thead>
                                <th style="border: 1px solid black; padding: 6px;" >Anno</th>
                                <th style="border: 1px solid black; padding: 6px;"># Fatture</th>
                                <th style="border: 1px solid black; padding: 6px;">#</th>
                                <th style="border: 1px solid black; padding: 6px;">Aperte</th>
                                <th style="border: 1px solid black; padding: 6px;">#</th>
                                <th style="border: 1px solid black; padding: 6px;">Pagate</th>
                                <th style="border: 1px solid black; padding: 6px;">gg Pagamento</th>
                                </thead>
                                <tbody>
                                """

            sorted_partner = sorted(partner_dict[_id].items(), key=lambda x: x[0], reverse=True)
            try:
                locale.setlocale(locale.LC_ALL, '{}.utf8'.format(context['lang']))
            except Exception as e:
                _logger.error("_compute_payment_prospect not locale.setlocale(locale.LC_ALL, '{}.utf8'.format(context['lang']))")
            for line in sorted_partner:
                year = line[0]
                sorted_partner_dict = line[1]
                domain = [('type', '=', 'out_invoice'), ('partner_id', '=', _id), ('state', '=', 'paid'), ('date_invoice', '>=', str(year)+'-01-01'), ('date_invoice', '<=', str(year)+'-12-31')]
                inv_ids = self.pool['account.invoice'].search(cr, uid, domain, context=context)
                inv_paid = self.pool['account.invoice'].read(cr, uid, inv_ids, ['payment_delta_days'], context)
                payment_days = list(map(lambda x: x['payment_delta_days'], inv_paid))
                avg = sum(payment_days) / len(payment_days) if payment_days else 0
                try:
                    open_amount_locale = locale.format_string("%.2f", sorted_partner_dict['open'], True)
                    paid_amount_locale = locale.format_string("%.2f", sorted_partner_dict['paid'], True)
                except Exception as e:
                    _logger.error("_compute_payment_prospect locale.format_string")
                    open_amount_locale = sorted_partner_dict['open']
                    paid_amount_locale = sorted_partner_dict['paid']

                html_table += """
                                <tr>
                                    <td style = "border-right: 1px solid black; border-left: 1px solid black; padding: 6px;">%s</td>
                                    <td style = "border-right: 1px solid black; border-left: 1px solid black; padding: 6px; text-align: right;">%s</td>
                                    <td style = "border-right: 1px solid black; border-left: 1px solid black; padding: 6px; text-align: right;">%s</td>
                                    <td style = "border-right: 1px solid black; border-left: 1px solid black; padding: 6px; text-align: right;">%s</td>
                                    <td style = "border-right: 1px solid black; border-left: 1px solid black; padding: 6px; text-align: right;">%s</td>
                                    <td style = "border-right: 1px solid black; border-left: 1px solid black; padding: 6px; text-align: right;">%s</td>
                                    <td style = "border-right: 1px solid black; border-left: 1px solid black; padding: 6px; text-align: right;">%s</td>
                                </tr>
                                """ % (year, sorted_partner_dict['num_invoice'], sorted_partner_dict['num_invoice_open'], open_amount_locale, sorted_partner_dict['num_invoice_paid'], paid_amount_locale, avg)
            res[_id] = html_table
        return res


    _columns = {
        'payment_ids': fields.function(_get_invoice_payment, string="All Open Payment", type='one2many',
                                       method=True, relation='account.move.line'),
        'overdue_credit': fields.function(_get_overdue_credit, fnct_search=_search_overdue_credit, string="Overdue Payment", type='float', method=True),
        'overdue_debit_positive': fields.function(_get_overdue_debit_positive, fnct_search=_search_overdue_debit_positive, string="Overdue positive", type='boolean', method=True),
        'last_overdue_credit_activity_date': fields.function(_get_credit_activity_history_last, method=True, string="Last Activity On", type='date'),
        'next_overdue_credit_activity_date': fields.function(_get_credit_activity_history_next, fnct_search=_search_next_overdue_credit_activity_date, method=True, string="Next Activity On", type='date'),
        'payment_prospect': fields.function(_compute_payment_prospect, string="Payment Prospect", type='char', method=True),
        'collections_out': fields.boolean('Recupero Presso Terzi'),
        'credit_phonecall_ids': fields.one2many('credit.phonecall', 'partner_id', 'Phonecalls'),
        'len_credit_phonecall_ids': fields.function(_get_len_credit_phonecall_ids, string="Numero Solleciti", type='integer', method=True),
        'excluding_recall': fields.boolean('Escluso dai richiami'),
    }

