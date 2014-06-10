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

from osv import osv


class ir_sequence(osv.osv):
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
        
