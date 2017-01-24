# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2013 Andrei Levin (andrei.levin at didotech.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
################################################################################

from osv import osv
from osv import fields
from tools.translate import _
import datetime


class ir_sequence(osv.osv):
    _inherit = 'ir.sequence'
    
    _columns = {
        'restart_on_next_year': fields.boolean(_('Restart on next year'), help=_('If selected, sequence will restart from 1 at the beginning of the new year'))
    }
    
    _defaults = {
        'restart_on_next_year': False,
    }
    
    ## This dictionary contains code to field mapping. Pay attention because
    ## the code can differ from the table name
    TABLE_TO_FIELD_MAP = {
        'sale.order': {'field': 'create_date', 'table': 'sale.order'},
        'purchase.order': {'field': 'date_order', 'table': 'purchase.order'},
        'stock.ddt': {'field': 'ddt_date', 'table': 'stock.picking'},
        'account.invoice': {'field': 'date_invoice', 'table': 'account.invoice'},
    }
    
    def _should_restart_sequence(self, cr, uid, seq, context=None):
        if not seq or not seq['restart_on_next_year']:
            return False
        
        if seq['code'] in self.TABLE_TO_FIELD_MAP:
            table = self.TABLE_TO_FIELD_MAP[seq['code']]['table']
            date_field = self.TABLE_TO_FIELD_MAP[seq['code']]['field']
            if table:
                documents = self.pool.get(table).search(cr, uid, ['!', (date_field, '=', False)], order=date_field + ' desc', limit=1)
                if documents:
                    document = self.pool.get(table).read(cr, uid, documents[0], (date_field,))
                    
                    if len(document[date_field]) == 19:
                        # Ex: 'create_date': '2013-06-14 15:36:25'
                        last_date = datetime.datetime.strptime(document[date_field], '%Y-%m-%d %H:%M:%S')
                    elif len(document[date_field]) == 10:
                        last_date = datetime.datetime.strptime(document[date_field], '%Y-%m-%d')
                    elif len(document[date_field]) == 26:
                        # Ex: 2013-06-14 19:52:36.273456
                        last_date = datetime.datetime.strptime(document[date_field], '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        return False
                    now = datetime.datetime.now()
                    if now.year > last_date.year:
                        return True
        return False
    
    def _next(self, cr, uid, seq_ids, context=None):
        if not seq_ids:
            return False
        if context is None:
            context = {}
        
        force_company = context.get('force_company')
        if not force_company:
            force_company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            
        sequences = self.read(cr, uid, seq_ids, ['code', 'company_id', 'implementation', 'number_next', 'number_increment', 'prefix', 'suffix', 'padding', 'restart_on_next_year'])
        preferred_sequences = [s for s in sequences if s['company_id'] and s['company_id'][0] == force_company ]
        seq = preferred_sequences[0] if preferred_sequences else sequences[0]
        if seq['implementation'] == 'standard':
            if self._should_restart_sequence(cr, uid, seq, context):
                self._alter_sequence(cr, seq_ids[0], seq['number_increment'], 1)
                seq['number_next'] = 1
            else:
                cr.execute("SELECT nextval('ir_sequence_%03d')" % seq['id'])
                seq['number_next'] = cr.fetchone()
        else:
            cr.execute("SELECT number_next FROM ir_sequence WHERE id=%s FOR UPDATE NOWAIT", (seq['id'],))
            if self._should_restart_sequence(cr, uid, seq, context):
                cr.execute("UPDATE ir_sequence SET number_next=1 WHERE id=%s ", (seq['id'],))
            else:
                cr.execute("UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s ", (seq['id'],))
        
        d = self._interpolation_dict()
        interpolated_prefix = self._interpolate(seq['prefix'], d)
        interpolated_suffix = self._interpolate(seq['suffix'], d)
        return interpolated_prefix + '%%0%sd' % seq['padding'] % seq['number_next'] + interpolated_suffix

    # def on_change_restart_on_next_year(self, cr, uid, ids, code, context=None):
    #     if not code in self.TABLE_TO_FIELD_MAP:
    #         return {'values': {'restart_on_next_year': False}, 'warning': {'title': _('Warning!'), 'message': _('Date field is not defined for "{code}" table. Please contact support for upgrade'.format(code=code))}}
    #     else:
    #         return {'values': {}}
