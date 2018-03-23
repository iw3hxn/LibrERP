# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp (<http://www.camptocamp.at>)
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

import time
from openerp.osv import orm, fields
from tools.translate import _
import logging
from openerp import SUPERUSER_ID


class ir_sequence_period(orm.Model):
    _name = 'account.sequence.period'
    _rec_name = "sequence_main_id"
    _columns = {
        "sequence_id": fields.many2one("ir.sequence", 'Sequence', required=True,
                                       ondelete='cascade'),
        "sequence_main_id": fields.many2one("ir.sequence", 'Main Sequence',
                                            required=True, ondelete='cascade'),
        "period_id": fields.many2one('account.period', 'Period',
                                     required=True, ondelete='cascade')
    }

    _sql_constraints = [
        ('main_id', 'CHECK (sequence_main_id != sequence_id)',
            'Main Sequence must be different from current !'),
    ]


class ir_sequence(orm.Model):
    _inherit = 'ir.sequence'
    _logger = logging.getLogger(__name__)

    _columns = {
        'auto_reset': fields.boolean('Auto Reset'),
        'reset_period': fields.selection(
            [('year', 'Every Year'), ('month', 'Every Month'), ('woy', 'Every Week'), ('day', 'Every Day'),
             ('h24', 'Every Hour'), ('min', 'Every Minute'), ('sec', 'Every Second')],
            'Reset Period', required=True),
        'reset_time': fields.char('Name', size=64, help=""),
        'reset_init_number': fields.integer('Reset Number', required=True, help="Reset number of this sequence"),
        'period_ids': fields.one2many('account.sequence.period',
                                      'sequence_main_id', 'Sequences'),
    }

    _defaults = {
        'auto_reset': False,
        'reset_period': 'month',
        'reset_init_number': 1,
    }
    
    def _abbrev(self, name, separator):
        return "".join(_(name).split(separator)[0])
    # end def _abbrev
    
    def next_by_id(self, cr, uid, sequence_id, context=None):
        if not context:
            context = {}
        """ Draw an interpolated string using the specified sequence."""
        self._logger.debug('next_by_id `%s` `%s`', sequence_id, context)
        self.check_read(cr, uid)
        # company_ids = self.pool.get('res.company').search(cr, uid, [], order='company_id', context=context) + [False]
        seq_id = sequence_id
        # create_sequence = ''
        journal_obj = self.pool['account.journal']
        journal = []
        if context.get('journal_id') and context['journal_id']:
            for journal in journal_obj.browse(cr, uid, [context['journal_id']], context=context):
                # create_sequence = journal.create_sequence
                if journal.create_sequence == 'create_period' and context.get('period_id') and context['period_id']:
                    per_seq_obj = self.pool['account.sequence.period']
                    per_seq_ids = per_seq_obj.search(cr, uid, [('sequence_main_id', '=', sequence_id), ('period_id', '=', context['period_id'])], context=context)
                    if per_seq_ids:
                        for per_seq in per_seq_obj.browse(cr, uid, per_seq_ids, context=context):
                            seq_id = per_seq.sequence_id.id
                    else:
                        period_obj = self.pool['account.period']
                        for period in period_obj.browse(cr, uid, [context['period_id']], context):
                            period_code = period.code
                            prefix = journal.sequence_id.prefix + period.fiscalyear_id.code  # +'-'+ period_code[2:6] +'-'
                        sequence_code = journal.sequence_id.code
                        vals = {
                            'code': sequence_code,
                            'name': journal.sequence_id.name + ' ' + period_code,
                            'prefix': prefix,
                            'padding': journal.sequence_id.padding,
                            'implementation': journal.sequence_id.implementation
                        }
                        seq_id = self.create(cr, uid, vals, context=context)
                        vals2 = {
                            'sequence_id': seq_id,
                            'sequence_main_id': sequence_id,
                            'period_id': context['period_id']
                        }
                        per_seq_obj.create(cr, uid, vals2, context=context)
                        
        if context.get('fiscalyear_id') and context['fiscalyear_id']:
            fy = context['fiscalyear_id']
            self._logger.debug('fy `%s`', fy)
            if fy:
                fy_seq_obj = self.pool['account.sequence.fiscalyear']
                fy_seq_ids = fy_seq_obj.search(cr, uid, [('sequence_main_id', '=', sequence_id), ('fiscalyear_id', '=', fy)], context=context)
                if fy_seq_ids:
                    for fy_s in fy_seq_obj.browse(cr, uid, fy_seq_ids, context=context):
                        seq_id = fy_s.sequence_id.id
                else:
                    fy_obj = self.pool['account.fiscalyear']
                    for fy in fy_obj.browse(cr, uid, [fy], context=context):
                        fy_name = fy.name
                        if not journal:
                            journal_ids = journal_obj.search(cr, uid, [('sequence_id', '=', sequence_id)], context=context)
                            if journal_ids:
                                journal = journal_obj.browse(cr, uid, journal_ids[0], context)
                            else:
                                raise orm.except_orm(_('No journal found'), '')
                        # prefix = journal.sequence_id.prefix + fy.code +'-' # removed (result as a duplication) but it make a bug for old installation #
                        if journal.sequence_id.prefix:
                            if fy.code:
                                prefix = journal.sequence_id.prefix.replace('/%(year)s/', '').replace('%(fy)s', fy.code)
                            else:
                                prefix = journal.sequence_id.prefix.replace('/%(year)s/', '').replace('%(fy)s', '') + '/'
                        else:
                            if fy.code:
                                prefix = fy.code + '/'
                            else:
                                prefix = ''

                    sequence_code = journal.sequence_id.code
                    vals = {
                        'code': sequence_code,
                        'name': journal.sequence_id.name + ' ' + fy_name,
                        'prefix': prefix,
                        'padding': journal.sequence_id.padding,
                        'implementation': journal.sequence_id.implementation
                    }
                    seq_id = self.create(cr, SUPERUSER_ID, vals, context=context)
                    vals2 = {
                        'sequence_id': seq_id,
                        'sequence_main_id': sequence_id,
                        'fiscalyear_id': context['fiscalyear_id']
                    }
                    fy_seq_obj.create(cr, SUPERUSER_ID, vals2, context=context)
                    
        self._logger.debug('next_by_id seq_id `%s`', seq_id)
        # ids = self.search(cr, uid, ['&',('id','=', sequence_id),('company_id','in',company_ids)])
        return self._next(cr, uid, seq_id, context)
    # end def next_by_id

    def _fy_code(self, cr, uid, context):
        if context and ('fiscalyear_id' in context) and context.get('fiscalyear_id', False):
            fy_id = context.get('fiscalyear_id', False)
            if fy_id:
                fiscalyear_obj = self.pool['account.fiscalyear']
                fy = fiscalyear_obj.browse(cr, uid, fy_id, context)
                return fy.sequence_code or fy.date_start[0:4]
        else:
            return time.strftime('%Y')
    # end def _fy_code
    
    def _month_code(self, cr, uid, context):
        if context and ('period_id' in context) and context.get('period_id', False):
            period_id = context.get('period_id', False)
            if period_id:
                period_obj = self.pool['account.period']
                period = period_obj.browse(cr, uid, period_id, context)
                # we assume that period code is YYYYMM
                # if FY starts with april then this should return YYMM
                return period.code[2]
        else:
            return ''
    # end def _fy_code

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.browse(cr, uid, ids, context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' ' + name
            
            fy_id = context.get('fiscalyear_id', False)
            if fy_id:
                fy_seq_code = self._fy_code(cr, uid, context)
                name = record['code'] + ' [' + fy_seq_code + ']'
            res.append((record['id'], name))
        return res
    # end def name_get

    def _journal(self, cr, uid, seq, context=None):
        journal_obj = self.pool['account.journal']
        jou = journal_obj.browse(cr, uid, journal_obj.search(cr, 1, [('sequence_id', '=', seq.id)], context=context), context)
        if jou:
            return jou[0]
        else:
            return False
    # end def _journal
    
    def _journal_name(self, cr, uid, seq, context=None):
        jou = self._journal(cr, uid, seq, context)
        if jou:
            return self._abbrev(jou.name, ' ')
        else:
            return ''
    # end def _journal_name
    
    def _seq_type(self, cr, uid, seq, context):
        seq_type_obj = self.pool['ir.sequence.type']
        ids = seq_type_obj.search(cr, uid, [('code', '=', seq.code)], context=context)
        if ids:
            return seq_type_obj.browse(cr, uid, ids[0], context)
        else:
            return False
    # end def _seq_type
    
    def _seq_type_name(self, cr, uid, seq, context):
        ty = self._seq_type(cr, uid, seq, context)
        return self._abbrev(ty.name, ' ')
    # end def _seq_type_name
    
    def _seq_type_code(self, cr, uid, seq, context):
        ty = self._seq_type(cr, uid, seq, context)
        return self._abbrev(ty.code, '.')
    # end def _seq_type_code
    
    def _next_seq(self, cr, uid, ids, context):
        seq = self.browse(cr, uid, ids, context)
        if isinstance(seq, list):
            seq = self.browse(cr, uid, ids, context)[0]
        
        self._logger.debug('_next_seq `%s`', seq)
        if seq.implementation == 'standard':
            current_time = ':'.join([seq.reset_period, self._interpolation_dict().get(seq.reset_period)])
            if seq['auto_reset'] and current_time != seq['reset_time']:
                cr.execute("UPDATE ir_sequence SET reset_time=%s WHERE id=%s ", (current_time, seq.id))
                self._alter_sequence(cr, seq.id, seq.number_increment, seq.reset_init_number)
                cr.commit()

            cr.execute("SELECT nextval('%s_%03d')" % (self._table, seq.id))
            seq.number_next = cr.fetchone()
        else:
            cr.execute("SELECT number_next FROM %s WHERE id=%s FOR UPDATE NOWAIT;" % (self._table, seq.id))
            seq.number_next = cr.fetchone()
            cr.execute("UPDATE %s SET number_next=number_next+number_increment WHERE id=%s" % (self._table, seq.id))
        return seq
    # end def _next_seq
    
    def _format(self, cr, uid, seq, context):
        d = self._interpolation_dict(context)
        d['fy'] = self._fy_code(cr, uid, context)
        d['pe'] = self._month_code(cr, uid, context)
        if self._seq_type(cr, uid, seq, context):
            d['stn'] = self._seq_type_name(cr, uid, seq, context)
            d['stc'] = self._seq_type_code(cr, uid, seq, context)
        d['jn'] = self._journal_name(cr, uid, seq, context)
        ty = self._seq_type(cr, uid, seq, context)
        if seq.prefix:
            _prefix = self._interpolate(seq.prefix, d)
        elif ty and ty.prefix_pattern:
            _prefix = self._interpolate(ty.prefix_pattern or '', d)
        else:
            _prefix = ''
        if seq.suffix:
            _suffix = self._interpolate(seq.suffix, d)
        elif ty and ty.suffix_pattern:
            _suffix = self._interpolate(ty.suffix_pattern or '', d)
        else:
            _suffix = ''
        return _prefix + ('%%0%sd' % seq.padding) % seq.number_next + _suffix
    # end def _format

    def _next(self, cr, uid, seq_ids, context=None):
        if not seq_ids:
            return False
        seq = self._next_seq(cr, uid, seq_ids, context)
        return self._format(cr, uid, seq, context)
    # end def _next

    def next_by_code(self, cr, uid, sequence_code, context=None):
        self._logger.debug('next_by_code `%s` `%s`', sequence_code, context)
        
        for user in self.pool.get('res.users').browse(cr, uid, [uid], context):
            self._logger.debug('next_by_code comp `%s`', user)
            # company_id = user.company_id.id
        
        # Disabled until bug in official stock addon is corrected
        # seq_ids = self.search(cr, uid, [('code', '=', sequence_code), ('company_id', '=', company_id)])
        seq_ids = self.search(cr, uid, [('code', '=', sequence_code)], context=context)
        if not seq_ids:
            seq_type_obj = self.pool['ir.sequence.type']
            seq_type_ids = seq_type_obj.search(cr, uid, [('code', '=', sequence_code)], context=context)
            if not seq_type_ids:
                raise orm.except_orm(
                    _('Integrity Error !'),
                    _('Missing sequence-code %s') % sequence_code
                )
            seq_type = seq_type_obj.browse(cr, uid, seq_type_ids[0], context)
            if seq_type.create_sequence == 'none':
                raise orm.except_orm(
                    _('Integrity Error !'),
                    _('Automatic creation not allowed for sequence-code %s with %s')
                    % (sequence_code, seq_type.create_sequence)
                )
            values = {
                'code': sequence_code,
                'name': self._abbrev(seq_type.name, ' '),
                # 'prefix':  # "%(stn)-",
                'padding': 3,
                'implementation': 'no_gap'
            }
            # we have to set uid = 1, because creating a sequence is granted to the module not to a user group
            new_id = self.create(cr, SUPERUSER_ID, values, context=context)
            seq = self._next_seq(cr, uid, new_id)
            return self._format(cr, uid, seq, context)
        else:
            return super(ir_sequence, self).next_by_code(cr, uid, sequence_code, context=context)
    # end def next_by_code
