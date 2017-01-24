# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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
from openerp.osv import orm, fields
from tools.translate import _
import logging


class account_bank_statement(orm.Model):
    _inherit = "account.bank.statement"
    _logger = logging.getLogger(__name__)


    # we have to copy the method because wen need to pass period_id and journal_id to next_by_id
    # rest is identical
    def button_confirm_bank(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        obj_seq = self.pool['ir.sequence']

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
                c = {'fiscalyear_id': st.period_id.fiscalyear_id.id, 'period_id': st.period_id.id, 'journal_id': st.journal_id.id}
                # c = {'fiscalyear_id': move.period_id.fiscalyear_id.id, 'period_id': move.period_id.id, 'journal_id': move.journal_id.id}
                if st.journal_id.sequence_id:
                    st_number = obj_seq.next_by_id(cr, uid, st.journal_id.sequence_id.id, context=c)
                else:
                    st_number = obj_seq.next_by_code(cr, uid, 'account.bank.statement', context=c)

            for line in st.move_line_ids:
                if line.state != 'valid':
                    raise orm.except_orm(_('Error !'),
                            _('The account entries lines are not in valid state.'))
            for st_line in st.line_ids:
                if st_line.analytic_account_id:
                    if not st.journal_id.analytic_journal_id:
                        raise orm.except_orm(_('No Analytic Journal !'), _("You have to assign an analytic journal on the '%s' journal!") % (st.journal_id.name,))
                if not st_line.amount:
                    continue
                st_line_number = self.get_next_st_line_number(cr, uid, st_number, st_line, context)
                self.create_move_from_st_line(cr, uid, st_line.id, company_currency_id, st_line_number, context)

            self.write(cr, uid, [st.id], {
                    'name': st_number,
                    'balance_end_real': st.balance_end
            }, context=context)
            self.log(cr, uid, st.id, _('Statement %s is confirmed, journal items are created.') % (st_number,))
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

        
class account_move(orm.Model):
    _inherit = "account.move"
    _logger = logging.getLogger(__name__)

    # we have to copy the method because wen need to pass period_id and journal_id to next_by_id
    # rest is identical
    def post(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)

        if not valid_moves:
            raise orm.except_orm(_('Integrity Error !'), _('You can not validate a non-balanced entry !\nMake sure you have configured payment terms properly !\nThe latest payment term line should be of the type "Balance" !'))
        obj_sequence = self.pool['ir.sequence']
        for move in self.browse(cr, uid, valid_moves, context=context):
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id, 'period_id': move.period_id.id, 'journal_id': move.journal_id.id}
                        new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                    else:
                        raise orm.except_orm(_('Error'), _('No sequence defined on the journal !'))

                if new_name:
                    self.write(cr, uid, [move.id], {'name': new_name}, context)

        cr.execute('UPDATE account_move '\
                   'SET state=%s '\
                   'WHERE id IN %s',
                   ('posted', tuple(valid_moves),))
        return True

        
    # # 20121010 Fgf NOT USED ANY MORE
    # def post_incompatible(self, cr, uid, ids, context=None):
    #     self._logger.debug('post move context `%s`', context)
    #     if not context:
    #         context= {}
    #     journal_id = context.get('journal_id')
    #     period_id = []
    #     if 'period_id' in context:
    #        period_id = [context.get('period_id')]
    #     self._logger.debug('post move period_id `%s`', period_id)
    #     invoice_obj = context.get('invoice')
    #     if invoice_obj and not journal_id:
    #        journal_id = invoice_obj.journal_id.id
    #     self._logger.debug('post move journal `%s`', journal_id)
    #     jour_obj = self.pool.get('account.journal')
    #     seq_obj  = self.pool.get('ir.sequence')
    #     if journal_id:
    #       for jour in jour_obj.browse(cr, uid, [journal_id] , context=context):
    #         self._logger.debug('post jour `%s` `%s`', jour, jour.sequence_id)
    #         if jour.sequence_id:
    #             main_seq_id = jour.sequence_id.id
    #         elif jour.create_sequence in ['create','create_fy']:
    #             prefix = jour.prefix_pattern or "".join(w[0] for w in _(jour.name).split(' '))
    #             values = \
    #                         { 'name'           : jour.name
    #                         , 'prefix'         : prefix
    #                         , 'padding'        : 3
    #                         , 'implementation' : 'no_gap'
    #                         }
    #             main_seq_id = seq_obj.create(cr, uid, values)
    #             jou_obj.write(cr, uid, [journal_id], {'sequence_id' : main_seq_id})
    #
    #         if jour.create_sequence == 'create_fy' :
    #             fy_seq_obj = self.pool.get('account.sequence.fiscalyear')
    #             period_obj = self.pool.get('account.period')
    #             if not period_id:
    #                self._logger.debug('per_id A')
    #                period_id = invoice_obj.period_id.id
    #                self._logger.debug('per_id B `%s`', period_id)
    #                if not period_id:
    #                    self._logger.debug('per_id C `%s`', period_id)
    #                    period_id = period_obj.find(cr, uid, invoice_obj.date_invoice, context)
    #                self._logger.debug('per_id D `%s`', period_id)
    #
    #             if not isinstance(period_id, list) :
    #                 period_id = [period_id]
    #             for period in period_obj.browse(cr, uid, period_id):
    #                 self._logger.debug('fy_id `%s`', period)
    #                 fy_id = period.fiscalyear_id.id
    #                 fy_code =  period.fiscalyear_id.code
    #                 self._logger.debug('fy_id a `%s`', fy_id)
    #             fy_seq = fy_seq_obj.search(cr, uid, [('fiscalyear_id','=', fy_id),('sequence_main_id','=',main_seq_id)])
    #             self._logger.debug('fy_seq_id `%s`', fy_seq)
    #             if not fy_seq:
    #                prefix = jour.prefix_pattern or "".join(w[0] for w in _(jour.name).split(' ')) + '-%(fy)s-'
    #
    #                values = \
    #                         { 'name'           : jour.name + ' ' +  fy_code
    #                         , 'prefix'         : prefix
    #                         , 'padding'        : 3
    #                         , 'implementation' : 'no_gap'
    #                         }
    #                fy_seq_id = seq_obj.create(cr, uid, values)
    #                fy_rel = \
    #                       { 'sequence_id'      : fy_seq_id
    #                       , 'sequence_main_id' : main_seq_id
    #                       , 'fiscalyear_id'    : fy_id
    #                       }
    #                self._logger.debug('fy_rel `%s``%s`', fy_rel, prefix)
    #                fy_seq_obj.create(cr, uid, fy_rel)
    #       #return True
    #     return super(account_move, self).post(cr, uid, ids, context)
