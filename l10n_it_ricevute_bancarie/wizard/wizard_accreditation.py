# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc

class riba_accreditation(osv.osv_memory):

    def _get_accreditation_journal_id(self, cr, uid, context=None):
        if context.get('active_model', False) == 'riba.distinta.line':
            return self.pool.get('riba.configurazione').get_default_value_by_distinta_line(cr, uid, 'accreditation_journal_id', context=context)
        if context.get('active_model', False) == 'riba.distinta':
            return self.pool.get('riba.configurazione').get_default_value_by_distinta(cr, uid, 'accreditation_journal_id', context=context)

    def _get_accreditation_account_id(self, cr, uid, context=None):
        res = False
        if context.get('active_model', False) == 'riba.distinta.line':
            res = self.pool.get('riba.configurazione').get_default_value_by_distinta_line(cr, uid, 'accreditation_account_id', context=context)
            if not res:
                res = self.pool.get('riba.configurazione').get_default_value_by_distinta_line(cr, uid, 'acceptance_account_id', context=context)
            return res
        if context.get('active_model', False) == 'riba.distinta':
            res = self.pool.get('riba.configurazione').get_default_value_by_distinta(cr, uid, 'accreditation_account_id', context=context)
            if not res:
                res = self.pool.get('riba.configurazione').get_default_value_by_distinta(cr, uid, 'acceptance_account_id', context=context)
            return res

    def _get_acceptance_account_id(self, cr, uid, context=None):
        res = False
        if context.get('active_model', False) == 'riba.distinta.line':
            return self.pool.get('riba.configurazione').get_default_value_by_distinta_line(cr, uid, 'acceptance_account_id', context=context)
        if context.get('active_model', False) == 'riba.distinta':
            return self.pool.get('riba.configurazione').get_default_value_by_distinta(cr, uid, 'acceptance_account_id', context=context)

    def _get_bank_account_id(self, cr, uid, context=None):
        if context.get('active_model', False) == 'riba.distinta.line':
            return self.pool.get('riba.configurazione').get_default_value_by_distinta_line(cr, uid, 'bank_account_id', context=context)
        if context.get('active_model', False) == 'riba.distinta':
            return self.pool.get('riba.configurazione').get_default_value_by_distinta(cr, uid, 'bank_account_id', context=context)

    def _get_bank_expense_account_id(self, cr, uid, context=None):
        if context.get('active_model', False) == 'riba.distinta.line':
            return self.pool.get('riba.configurazione').get_default_value_by_distinta_line(cr, uid, 'bank_expense_account_id', context=context)
        if context.get('active_model', False) == 'riba.distinta':
            return self.pool.get('riba.configurazione').get_default_value_by_distinta(cr, uid, 'bank_expense_account_id', context=context)

    def _get_accreditation_amount(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not context.get('active_id', False):
            return False
        amount = 0.0
        config = False
        if context.get('active_model', False) == 'riba.distinta.line':
            distinta_line_pool = self.pool.get('riba.distinta.line')
            distinta_lines = distinta_line_pool.browse(cr, uid, context['active_ids'], context=context)
            for line in distinta_lines:
                if not config:
                    config = line.distinta_id.config
                if line.distinta_id.config != config:
                    raise osv.except_osv(_('Error'), _('Accredit only one bank configuration is possible'))
                if line.state in ['confirmed', 'accredited']:
                    amount += line.amount
        elif context.get('active_model', False) == 'riba.distinta':
            distinta_pool = self.pool.get('riba.distinta')
            distinta = distinta_pool.browse(cr, uid, context['active_id'], context=context)
            for line in distinta.line_ids:
                if line.tobeaccredited and line.state in ['confirmed', 'accredited']:
                    amount += line.amount
        return amount

    _name = "riba.accreditation"
    _description = "Bank accreditation"
    _columns = {
        'accreditation_journal_id': fields.many2one('account.journal', "Accreditation journal",
            domain=[('type', '=', 'bank')]),
        'accreditation_account_id': fields.many2one('account.account', "Ri.Ba. bank account"),
        'acceptance_account_id': fields.many2one('account.account', "Ri.Ba. acceptance account"),
        'accreditation_amount': fields.float('Credit amount'),
        'bank_account_id': fields.many2one('account.account', "Bank account",
            domain=[('type', '=', 'liquidity')]),
        'bank_amount': fields.float('Versed amount'),
        'bank_expense_account_id': fields.many2one('account.account', "Bank Expenses account"),
        'expense_amount': fields.float('Expenses amount'),
        'date_accreditation': fields.date('Accreditation date'),
        }

    _defaults = {
        'accreditation_journal_id': _get_accreditation_journal_id,
        'accreditation_account_id': _get_accreditation_account_id,
        'acceptance_account_id': _get_acceptance_account_id,
        'bank_account_id': _get_bank_account_id,
        'bank_expense_account_id': _get_bank_expense_account_id,
        'accreditation_amount': _get_accreditation_amount,
        }

    def skip(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wf_service = netsvc.LocalService("workflow")
        active_id = context and context.get('active_id', False) or False
        if not active_id:
            raise osv.except_osv(_('Error'), _('No active ID found'))
        wf_service.trg_validate(
            uid, 'riba.distinta', active_id, 'accredited', cr)
        if context.get('active_model', False) == 'riba.distinta.line':
            active_ids = context and context.get('active_ids', False) or False
            if not active_ids:
                raise osv.except_osv(_('Error'), _('No active IDS found'))
            distinta_line_pool = self.pool.get('riba.distinta.line')
            distinta_lines = distinta_line_pool.browse(cr, uid, active_ids, context=context)
            for line in distinta_lines:
                if not line.state == "accredited":
                    line.write({'state': 'accredited'})
        return {'type': 'ir.actions.act_window_close'}

    def create_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wf_service = netsvc.LocalService("workflow")
        ref = ''
        if context.get('active_model', False) == 'riba.distinta':
            active_id = context and context.get('active_id', False) or False
            if not active_id:
                raise osv.except_osv(_('Error'), _('No active ID found'))
            distinta_pool = self.pool.get('riba.distinta')
            distinta = distinta_pool.browse(cr, uid, active_id, context=context)
            if not context.get('accruement', False) and not distinta.config.accreditation_account_id:
                context.update({'accruement': True, 'accreditation_accruement': True})
            ref = distinta.name
        move_pool = self.pool.get('account.move')
#        move_line_pool = self.pool.get('account.move.line')
        
        if context.get('active_model', False) == 'riba.distinta.line':
            distinta_line_pool = self.pool.get('riba.distinta.line')
            active_ids = context and context.get('active_ids', False)
            if not active_ids:
                raise osv.except_osv(_('Error'), _('No active IDS found'))
            distinta_lines = distinta_line_pool.browse(cr, uid, active_ids, context=context)
            last_id = ''
            for line in distinta_lines:
                if line.distinta_id.id != last_id:
                    ref += line.distinta_id.name + ' '
                last_id = line.distinta_id.id
            if not context.get('accruement', False) and not line.distinta_id.config.accreditation_account_id:
                context.update({'accruement': True, 'accreditation_accruement': True})
        
        wizard = self.browse(cr, uid, ids)[0]
        if not wizard.accreditation_journal_id or not wizard.date_accreditation:
            raise osv.except_osv(_('Error'), _('Every account is mandatory'))
        if not context.get('accruement', False):
            if not wizard.bank_account_id or not wizard.accreditation_account_id:
                raise osv.except_osv(_('Error'), _('Bank account is mandatory for accreditation move'))
        if context.get('accruement', False):
            if not wizard.acceptance_account_id and not wizard.accreditation_account_id:
                raise osv.except_osv(_('Error'), _('Acceptance or accredit account is mandatory for accrue move'))
        date_accreditation = wizard.date_accreditation
        
        move_vals = {
            'ref': _('Accreditation Ri.Ba. %s') % ref,
            'journal_id': wizard.accreditation_journal_id.id,
            'date': date_accreditation,
            'line_id': [
                (0, 0, {
                    'name': _('Bank'),
                    'account_id': context.get('accruement', False) and not context.get('accreditation_accruement', False) and wizard.accreditation_account_id.id or wizard.bank_account_id.id,
                    'debit': wizard.bank_amount,
                    'credit': 0.0,
                    'date': date_accreditation,
                    }),
                (0, 0, {
                    'name': _('Credit'),
                    'account_id': context.get('accruement', False) and wizard.acceptance_account_id.id or wizard.accreditation_account_id.id,
                    'credit': wizard.accreditation_amount,
                    'debit': 0.0,
                    'date': date_accreditation,
                    }),
#                 (0, 0, {
#                     'name': _('Bank'),
#                     'account_id': wizard.bank_expense_account_id.id,
#                     'debit': wizard.expense_amount,
#                     'credit': 0.0,
#                     'date': date_accreditation,
#                     }),
                ]
            }
        move_id = move_pool.create(cr, uid, move_vals, context=context)
        accredited = True
        accrued = True
        if context.get('active_model', False) == 'riba.distinta':
            if context.get('accruement', False):
                for line in distinta.line_ids:
                    if line.tobeaccredited and not line.state == "accrued":
                        line.write({'accruement_move_id': move_id,
                                    'state': 'accrued'})
                    if not line.tobeaccredited:
                            accrued = False
                if accrued:
                    wf_service.trg_validate(
                        uid, 'riba.distinta', active_id, 'accrued', cr)
            else:
                for line in distinta.line_ids:
                    if line.tobeaccredited and not line.state == "accredited":
                        line.write({'accreditation_move_id': move_id,
                                    'state': 'accredited'})
                    if not line.tobeaccredited:
                            accredited = False
                if accredited:
                    wf_service.trg_validate(
                        uid, 'riba.distinta', active_id, 'accredited', cr)
        if context.get('active_model', False) == 'riba.distinta.line':
            if context.get('accruement', False):
                for line in distinta_lines:
                    if not line.state == "accrued":
                        line.write({'accruement_move_id': move_id,
                                    'state': 'accrued'})
            else:
                for line in distinta_lines:
                    if not line.state == "accredited":
                        line.write({'accreditation_move_id': move_id,
                                    'state': 'accredited'})
            #TODO: if all lines of a distinta are accredited, set distinta accredited
        return {
            'name': _('Accreditation Entry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_id or False,
        }
