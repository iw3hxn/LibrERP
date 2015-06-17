# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Didotech srl
#    (<http://www.didotech.com>). 
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class account_bank_statement_line(orm.Model):
    _inherit = 'account.bank.statement.line'

    _columns = {
        'move_line_id': fields.many2one('account.move.line', 'Account move line'),
    }


class account_bank_statement(orm.Model):
    _inherit = 'account.bank.statement'

    def balance_check(self, cr, uid, st_id, journal_type='bank', context=None):
        st = self.browse(cr, uid, st_id, context=context)
        if st.balance_end_real != 0.0:
            super(account_bank_statement, self).balance_check(cr, uid, st_id, journal_type='bank', context=context)
        return True

    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, st_line_number, move_id, context=None):
        if context is None:
            context = {}
        res_currency_obj = self.pool['res.currency']
        account_move_line_obj = self.pool['account.move.line']
        account_bank_statement_line_obj = self.pool['account.bank.statement.line']
        st_line = account_bank_statement_line_obj.browse(cr, uid, st_line_id, context=context)
        st = st_line.statement_id

        context.update({'date': st_line.date})

        acc_cur = ((st_line.amount <= 0) and st.journal_id.default_debit_account_id) or st_line.account_id
        context.update({
                'res.currency.compute.account': acc_cur,
            })
        amount = res_currency_obj.compute(cr, uid, st.currency.id,
                company_currency_id, st_line.amount, context=context)

        val = {
            'name': st_line.ref or '/',
            'date': st_line.date,
            'ref': st_line_number or '/',
            'move_id': move_id,
            'partner_id': ((st_line.partner_id) and st_line.partner_id.id) or False,
            'account_id': (st_line.account_id) and st_line.account_id.id,
            'credit': ((amount > 0) and amount) or 0.0,
            'debit': ((amount < 0) and -amount) or 0.0,
            'statement_id': st.id,
            'journal_id': st.journal_id.id,
            'period_id': st.period_id.id,
            'currency_id': st.currency.id,
            'analytic_account_id': st_line.analytic_account_id and st_line.analytic_account_id.id or False
        }

        if st.currency.id != company_currency_id:
            amount_cur = res_currency_obj.compute(cr, uid, company_currency_id,
                        st.currency.id, amount, context=context)
            val['amount_currency'] = -amount_cur

        if st_line.account_id and st_line.account_id.currency_id and st_line.account_id.currency_id.id <> company_currency_id:
            val['currency_id'] = st_line.account_id.currency_id.id
            amount_cur = res_currency_obj.compute(cr, uid, company_currency_id,
                    st_line.account_id.currency_id.id, amount, context=context)
            val['amount_currency'] = -amount_cur

        move_line_id = account_move_line_obj.create(cr, uid, val, context=context)

        return move_line_id

    def button_confirm_bank(self, cr, uid, ids, context=None):
        obj_seq = self.pool['ir.sequence']
        if context is None:
            context = {}
        account_move_obj = self.pool['account.move']
        account_move_line_obj = self.pool['account.move.line']
        account_bank_statement_line_obj = self.pool['account.bank.statement.line']
        
        for st in self.browse(cr, uid, ids, context=context):
            j_type = st.journal_id.type
            company_currency_id = st.journal_id.company_id.currency_id.id
            if not self.check_status_condition(cr, uid, st.state, journal_type=j_type):
                continue

            self.balance_check(cr, uid, st.id, journal_type=j_type, context=context)
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise orm.except_orm(_('Configuration Error !'),
                        _('Please verify that an account is defined in the journal.'))

            if not st.name == '/':
                st_number = st.name
            else:
                # 1 row copied from c2c_fy - because we need to overwrite without super()
                c = {'fiscalyear_id': st.period_id.fiscalyear_id.id, 'period_id': st.period_id.id, 'journal_id': st.journal_id.id}
                if st.journal_id.sequence_id:
                    st_number = obj_seq.next_by_id(cr, uid, st.journal_id.sequence_id.id, context=c)
                else:
                    st_number = obj_seq.next_by_code(cr, uid, 'account.bank.statement', context=c)

            for line in st.move_line_ids:
                if line.state != 'valid':
                    raise orm.except_orm(_('Error !'),
                            _('The account entries lines are not in valid state.'))

            move_id = account_move_obj.create(cr, uid, {
                'journal_id': st.journal_id.id,
                'period_id': st.period_id.id,
                'date': st.date,
                'name': st_number or '/',
                'ref': st_number or '/',
            }, context=context)

            to_be_reconciled = []
            st_line_sum = 0.0
            for st_line in st.line_ids:
                if st_line.analytic_account_id:
                    if not st.journal_id.analytic_journal_id:
                        raise orm.except_orm(_('No Analytic Journal !'), _("You have to assign an analytic journal on the '%s' journal!") % (st.journal_id.name,))
                if not st_line.amount:
                    continue
                st_line_number = st_number + '/' + str(st_line.sequence)
                move_line_id = self.create_move_from_st_line(cr, uid, st_line.id, company_currency_id, st_line_number, move_id, context)
                if move_line_id:
                    to_be_reconciled.append([move_line_id, st_line.move_line_id.id])
                st_line_sum += st_line.amount
                account_bank_statement_line_obj.write(cr, uid, [st_line.id], {'move_ids': [(4, move_id, False)]})

            if st_line_sum >= 0:
                account_id = st.journal_id.default_credit_account_id.id
            else:
                account_id = st.journal_id.default_debit_account_id.id

            # create total counterpart
            amount_currency = False
            currency_id = False
            if st.currency.id <> company_currency_id:
                amount_currency = st_line_sum
                currency_id = st.currency.id
            move_line_id = account_move_line_obj.create(cr, uid, {
                'name': st.name or '/',
                'date': st.date,
                'ref': st_number or '/',
                'move_id': move_id,
                'account_id': account_id,
                'credit': ((st_line_sum < 0) and -st_line_sum) or 0.0,
                'debit': ((st_line_sum > 0) and st_line_sum) or 0.0,
                'statement_id': st.id,
                'journal_id': st.journal_id.id,
                'period_id': st.period_id.id,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
                }, context=context)

            for line in account_move_line_obj.browse(cr, uid, [x.id for x in
                    account_move_obj.browse(cr, uid, move_id,
                        context=context).line_id],
                    context=context):
                if line.state != 'valid':
                    raise orm.except_orm(_('Error !'),
                            _('Journal item "%s" is not valid.') % line.name)

            for reconcile_ids in to_be_reconciled:
                account_move_line_obj.reconcile_partial(cr, uid, reconcile_ids, context=context)

            # Bank statements will not consider boolean on journal entry_posted
            account_move_obj.post(cr, uid, [move_id], context=context)
            self.write(cr, uid, [st.id], {
                    'name': st_number,
                    'balance_end_real': st.balance_end
            }, context=context)

            self.log(cr, uid, st.id, _('Statement %s is confirmed, journal items are created.') % (st_number,))
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)
