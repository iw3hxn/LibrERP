# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
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

from openerp.osv import fields, orm, osv
from openerp.tools.translate import _

PAYMENT_TERM_TYPE_SELECTION = [
    ('BB', 'Bonifico Bancario'),
    ('BP', 'Bonifico Postale'),
    ('RD', 'Rimessa Diretta'),
    ('RB', 'Ricevuta Bancaria'),
    ('F4', 'F24'),
    ('PP', 'Paypal'),
    ('CC', 'Carta di Credito'),
    ('CO', 'Contrassegno'),
    ('CN', 'Contanti'),
]

default_row_colors = ['black', 'forestgreen', 'darkblue', 'brown', 'blue', 'cadetblue', 'fuchsia', 'orange', 'green']


class account_move_line(orm.Model):

    _inherit = 'account.move.line'

    def _residual(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.read(cr, uid, ids, ['debit', 'credit'], context=context):
            res[line['id']] = line['debit'] - line['credit']
        return res

    def _direction(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.read(cr, uid, ids, ['debit', 'credit'], context=context):
            if line['debit']:
                res[line['id']] = '+'
            elif line['credit']:
                res[line['id']] = '-'
            else:
                res[line['id']] = '='
        return res

    def _get_bank(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, False)
        context['only_iban'] = True

        cr.execute("""SELECT 
              account_move_line.id, 
              account_invoice.partner_bank_id
            FROM 
              public.account_invoice, 
              public.account_move_line
            WHERE 
              account_move_line.stored_invoice_id = account_invoice.id AND
             
              account_invoice.partner_bank_id IS NOT NULL AND
              account_move_line.id in ({move_ids})
        """.format(move_ids=', '.join([str(move_id) for move_id in ids])))
        val = cr.fetchall()

        for el in val:
            res[el[0]] = el[1]

        return res

    def _hook_get_invoice_line(self, cr, uid, line, context):
        return False

    def _get_invoice(self, cr, uid, ids, field_name, arg, context=None):
        invoice_pool = self.pool['account.invoice']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            inv_ids = invoice_pool.search(cr, 1, [('move_id', '=', line.move_id.id)], context=context)
            if len(inv_ids) > 1:
                raise orm.except_orm(_('Error'), _('Incongruent data: move %s has more than one invoice') % line.move_id.name)
            if inv_ids:
                res[line.id] = inv_ids[0]
            else:
                res[line.id] = self._hook_get_invoice_line(cr, uid, line, context)
        return res

    def _get_day(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.date_maturity:
                res[line.id] = line.date_maturity
            else:
                res[line.id] = False
        return res
        
    def _get_move_lines(self, cr, uid, ids, context=None):
        invoice_pool = self.pool['account.invoice']
        res = []
        for invoice in invoice_pool.browse(cr, uid, ids, context=context):
            if invoice.move_id:
                for line in invoice.move_id.line_id:
                    if line.id not in res:
                        res.append(line.id)
        return res

    def _balance(self, cr, uid, ids, name, arg, context=None):
        res = {}
        # TODO group the foreach in sql
        for id in ids:
            cr.execute('SELECT date,account_id FROM account_move_line WHERE id=%s', (id,))
            dt, acc = cr.fetchone()
            cr.execute('SELECT SUM(debit-credit) FROM account_move_line WHERE account_id = %s AND (date<%s OR (date=%s AND id<=%s))', (acc, dt, dt, id))
            res[id] = cr.fetchone()[0]
        return res

    # todo write this function, speedup of 20% but need to write also search function, at the moment not necessary
    # def _get_stored_invoice_vals(self, cr, uid, ids, field_name, arg, context=None):
    #     res = {}
    #     for move in self.browse(cr, uid, ids, context):
    #         res[move.id] = {
    #             'invoice_origin': False,
    #             'invoice_date': False,
    #             'payment_term_id': False,
    #             'payment_term_type': ''
    #         }
    #         if move.stored_invoice_id:
    #             res[move.id] = {
    #                 'invoice_origin': move.stored_invoice_id.origin,
    #                 'invoice_date': move.stored_invoice_id.date_invoice,
    #                 'payment_term_id': move.stored_invoice_id.payment_term and move.stored_invoice_id.payment_term.id or False,
    #                 'payment_term_type': move.stored_invoice_id.payment_term and move.stored_invoice_id.payment_term.type or '',
    #             }
    #     return res

    # def _get_running_balance(self, cr, uid, ids, name, args, context):
    #     res = {}
    #     balance = 0
    #     order_search = context.get('order', 'date_maturity asc')
    #     new_ids = self.search(cr, uid, [('id', 'in', ids)], order=order_search, context=context)
    #     # for line in self.read(cr, uid, new_ids, ['debit', 'credit'], context=context):
    #     for line_id in new_ids:
    #         line = self.read(cr, uid, line_id, ['debit', 'credit'], context=context)
    #         balance += line['debit'] - line['credit']
    #         res[line['id']] = balance
    #     return res

    def _get_running_balance(self, cr, uid, ids, name, args, context):
        res = {}
        balance = 0
        for line_id in ids[::-1]:
            line = self.read(cr, uid, line_id, ['debit', 'credit'], context=context)
            balance += line['debit'] - line['credit']
            res[line['id']] = balance
        return res

    def get_color(self, cr, uid, ids, field_name, arg, context):
        res = {}
        color = {}

        pointer = 0
        key = context.get('color', 'date_maturity')
        if key == 'reconcile_function_id':
            pointer += 1
        for line in self.read(cr, uid, ids, [key, 'state'], context):
            line_key = line[key]
            if line['state'] == 'draft':
                res[line['id']] = 'red'
                continue
            if not line_key:
                res[line['id']] = default_row_colors[0]
                continue
            if line_key not in color:
                color[line[key]] = default_row_colors[pointer]
                pointer += 1
                if pointer > (len(default_row_colors) - 1):
                    pointer = 0
                    if key == 'reconcile_function_id':
                        pointer += 1
            res[line['id']] = color[line[key]]
        return res

    _columns = {
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True, ),
        'invoice_origin': fields.related('stored_invoice_id', 'origin', type='char', string='Source Doc', store=False),
        'invoice_date': fields.related('stored_invoice_id', 'date_invoice', type='date', string='Invoice Date', store=False),
        'payment_term_id': fields.related('stored_invoice_id', 'payment_term', type='many2one', string='Payment Term', store=False, relation="account.payment.term"),
        'payment_term_type': fields.related('stored_invoice_id', 'payment_term', 'type', type="selection", selection=PAYMENT_TERM_TYPE_SELECTION, string="Payment Type", store=False),
        # 'invoice_origin': fields.function(_get_stored_invoice_vals, method=True, multi='stored_invoice_vals', type='char', string='Source Doc', store=False),
        # 'invoice_date': fields.function(_get_stored_invoice_vals, method=True, multi='stored_invoice_vals', type='date', string='Invoice Date',
        #                                store=False),
        # 'payment_term_id': fields.function(_get_stored_invoice_vals, method=True, multi='stored_invoice_vals', type='many2one', string='Payment Term',
        #                                   store=False, relation="account.payment.term"),
        # 'payment_term_type': fields.function(_get_stored_invoice_vals, method=True, multi='stored_invoice_vals', type="selection",
        #                                     selection=PAYMENT_TERM_TYPE_SELECTION, string="Payment Type", store=False),
        'partner_ref': fields.related('partner_id', 'ref', type='char', string='Partner Ref', store=False),
        'bank_id': fields.function(_get_bank, method=True, string="Bank", type="many2one", relation="res.partner.bank",
                                   store=False),
        'stored_invoice_id': fields.function(_get_invoice, method=True, string="Invoice", type="many2one", relation="account.invoice",
                                             store={
                                                 'account.move.line': (lambda self, cr, uid, ids, c={}: ids, ['move_id'], 10),
                                                 'account.invoice': (_get_move_lines, ['move_id'], 10),
                                             }),
        'day': fields.function(_get_day, method=True, string="Day", type="char", size=16,
                               store={
                                   'account.move.line': (lambda self, cr, uid, ids, c={}: ids, ['date_maturity'], 10),
                               }),
        'residual': fields.function(_residual, method=True, string='Residual', type='float', store=False),
        'direction': fields.function(_direction, method=True, string='Direction', type='char', store=False),
        'balance': fields.function(_balance, method=True, string='Balance', type='float', store=False),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'running_balance': fields.function(_get_running_balance, method=True, string="Running Balance", store=False),
    }

    _order = "date desc, ref asc, move_id asc, id asc"
    # _order = "date_maturity desc, date desc, ref asc, move_id asc, id asc"
    # _order = "date_maturity desc, date asc, move_id asc, id asc"
    # _sql_constraints = [
    #     ('maturity_date', "CHECK (date_maturity>='1900-01-01')", 'Wrong date maturity in accounting entry !'),
    # ]

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context={}, toolbar=False, submenu=False):
        view_payments_tree_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'account_due_list', 'view_payments_tree')
        view_payments_tree2_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'account_due_list', 'view_account_ledger_tree')
        if view_id == view_payments_tree_id[1] or view_id == view_payments_tree2_id[1]:
            # Use due list
            result = super(orm.Model, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        else:
            # Use special views for account.move.line object (for ex. tree view contains user defined fields)
            result = super(account_move_line, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        return result

