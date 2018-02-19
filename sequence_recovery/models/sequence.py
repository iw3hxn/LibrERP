# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Andrea Cometa - Perito informatico
#    All Rights Reserved
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
from openerp.osv import orm, fields


class ir_sequence_recovery(orm.Model):
    _name = "ir.sequence_recovery"
    _description = "ir.sequence_recovery"

    _columns = {
        'active': fields.boolean('Active'),
        'name': fields.char('Class Name', size=32),
        'sequence_id': fields.many2one('ir.sequence', 'Sequence'),
        'sequence': fields.char('Sequence Number', size=32),
        'date': fields.date('Date'),
        'create_uid': fields.many2one('res.users', 'Creation User'),
        'write_uid': fields.many2one('res.users', 'Deactivate User'),
    }

    _defaults = {
        'date': fields.date.context_today,
        'active': True
    }

    _order = "date, sequence asc, name"

    def set(self, cr, uid, ids, class_name, sequence_field='name',
            sequence_code='', sequence_id=False, context=None):
        # ----- init
        class_obj = self.pool.get(class_name)
        recovery_ids = []
        # ----- Extract the sequence id if it's not passed
        seq_id = sequence_id
        if sequence_code and not sequence_id:
            sequence_code_ids = self.pool['ir.sequence'].search(
                cr, uid, [('name', '=', sequence_code)], context=context)
            if sequence_code_ids:
                seq_id = sequence_code_ids[0]
        # ----- For each record deleted save the parameters
        for o in class_obj.browse(cr, uid, ids, context):
            sequence = o[sequence_field]
            if sequence:
                vals = {
                    'name': class_name,
                    'sequence': sequence,
                    'sequence_id': seq_id,
                }
                recovery_ids = self.search(cr, uid, [('name', '=', class_name), ('sequence', '=', sequence), ('sequence_id', '=', seq_id)], context=context)
                if recovery_ids:
                    recovery_id = recovery_ids[0]
                else:
                    recovery_id = self.create(cr, uid, vals, context)
                recovery_ids.append(recovery_id)
        return recovery_ids


class ir_sequence(orm.Model):
    _name = "ir.sequence"
    _inherit = "ir.sequence"

    def next_by_id(self, cr, uid, sequence_id, context=None):
        # import pdb; pdb.set_trace()
        recovery_obj = self.pool['ir.sequence_recovery']
        recovery_ids = recovery_obj.search(cr, uid, [('sequence_id', '=', sequence_id)], context=context)
        if recovery_ids:
            # ----- If found it, it recoveries the sequence and return it
            recovery_id = recovery_ids[0]
            sequence = recovery_obj.browse(cr, uid, recovery_id, context).sequence
            recovery_obj.write(cr, uid, recovery_id, {'active': False}, context)
        else:
            sequence = super(ir_sequence, self).next_by_id(cr, uid, sequence_id, context)
        return sequence

    def next_by_code(self, cr, uid, sequence_code, context=None):
        # import pdb; pdb.set_trace()
        recovery_obj = self.pool['ir.sequence_recovery']
        recovery_ids = recovery_obj.search(cr, uid, [('name', '=', sequence_code)], context=context)
        if recovery_ids:
            # ----- If found it, it recoveries the sequence and return it
            recovery_id = recovery_ids[0]
            sequence = recovery_obj.browse(cr, uid, recovery_id, context).sequence
            recovery_obj.write(cr, uid, recovery_id, {'active': False}, context)
        else:
            sequence = super(ir_sequence, self).next_by_code(cr, uid, sequence_code, context)
        return sequence
