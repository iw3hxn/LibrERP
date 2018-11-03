# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
import time
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class ir_sequence(orm.Model):
    _inherit = 'ir.sequence'
    
    def current_number(self, cr, uid, sequence_id):
        assert isinstance(sequence_id, (int, long))
        sequence = self.browse(cr, uid, sequence_id)
        next_number = self._get_number_next_actual(cr, uid, [sequence_id], 'number_next_actual', None)
        
        return next_number[sequence_id] - sequence.number_increment
        
    def go_back(self, cr, uid, sequence_id, steps_back=1):
        assert isinstance(sequence_id, (int, long))
        sequence = self.browse(cr, uid, sequence_id)
        
        current_number = self.current_number(cr, uid, sequence_id)
        
        if current_number > sequence.number_increment * (steps_back - 1):
            number_next = current_number - sequence.number_increment * (steps_back - 1)
        else:
            number_next = sequence.number_increment
        
        if sequence.implementation == 'standard':
            self._alter_sequence(cr, sequence_id, sequence.number_increment, number_next=number_next)
        else:
            # sequence.implementation == 'no_gap':
            self.write(cr, uid, sequence_id, {'number_next': number_next})

    def create(self, cr, uid, values, context=None):
        if context and context.get('code', False):
            values['code'] = context['code']
        return super(ir_sequence, self).create(cr, uid, values, context)

    def _interpolation_dict(self, context=None):
        # add possibility to pass context, if set a 'date' field it will be used instead of current date
        if context is None:
            context = {}
        if context.get('date', False):
            date = context.get('date')
            t = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
            res = {
                'year': t.strftime('%Y'),
                'month': t.strftime('%m'),
                'day': t.strftime('%d'),
                'y': t.strftime('%y'),
                'doy': t.strftime('%j'),
                'woy': t.strftime('%W'),
                'weekday': t.strftime('%w'),
                'h24': t.strftime('%H'),
                'h12': t.strftime('%I'),
                'min': t.strftime('%M'),
                'sec': t.strftime('%S'),
                }
        else:
            t = time.localtime()  # Actually, the server is always in UTC.
            res = {
                'year': time.strftime('%Y', t),
                'month': time.strftime('%m', t),
                'day': time.strftime('%d', t),
                'y': time.strftime('%y', t),
                'doy': time.strftime('%j', t),
                'woy': time.strftime('%W', t),
                'weekday': time.strftime('%w', t),
                'h24': time.strftime('%H', t),
                'h12': time.strftime('%I', t),
                'min': time.strftime('%M', t),
                'sec': time.strftime('%S', t),
            }
        return res

    # def _next(self, cr, uid, seq_ids, context=None):
    #     if not seq_ids:
    #         return False
    #     if context is None:
    #         context = self.pool['res.users'].context_get(cr, uid)
    #
    #     if not isinstance(seq_ids, (list, tuple)):
    #         seq_ids = [seq_ids]
    #
    #     force_company = context.get('force_company')
    #     if not force_company:
    #         force_company = self.pool['res.users'].browse(cr, uid, uid, context).company_id.id
    #     sequences = self.read(cr, uid, seq_ids, ['company_id', 'implementation', 'number_next', 'prefix', 'suffix', 'padding'])
    #     preferred_sequences = [s for s in sequences if s['company_id'] and s['company_id'][0] == force_company]
    #     seq = preferred_sequences[0] if preferred_sequences else sequences[0]
    #     if seq['implementation'] == 'standard':
    #         cr.execute("SELECT nextval('ir_sequence_%03d')" % seq['id'])
    #         seq['number_next'] = cr.fetchone()
    #     else:
    #         cr.execute("SELECT number_next FROM ir_sequence WHERE id=%s FOR UPDATE NOWAIT", (seq['id'],))
    #         cr.execute("UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s ", (seq['id'],))
    #     d = self._interpolation_dict(context)  # only this row is modified from standard ocb
    #     interpolated_prefix = self._interpolate(seq['prefix'], d)
    #     interpolated_suffix = self._interpolate(seq['suffix'], d)
    #     return interpolated_prefix + '%%0%sd' % seq['padding'] % seq['number_next'] + interpolated_suffix
