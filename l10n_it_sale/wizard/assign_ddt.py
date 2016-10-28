# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2010 Associazione OpenERP Italia
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
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID
import time


class wizard_assign_ddt(orm.TransientModel):
    _name = "wizard.assign.ddt"

    # def _next_ddt(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = self.pool['res.users'].context_get(cr, uid)
    #     res = {}
    #     picking_obj = self.pool['stock.picking']
    #     import pdb; pdb.set_trace()
    #     for wizard in self.browse(cr, uid, ids, context=context):
    #         for picking in picking_obj.browse(cr, uid, context.get('active_ids', []), context=context):
    #             if picking.ddt_number:
    #                 ddt_number = _('DTT number already assigned')
    #             elif picking.stock_journal_id.ddt_sequence:
    #                 ddt_number = self.pool['ir.sequence']._get_number_next_actual(cr, uid, [picking.stock_journal_id.ddt_sequence.id], 'number_next_actual', None)
    #             else:
    #                 ddt_number = self.pool['ir.sequence'].get(cr, uid, 'stock.ddt')
    #             res[wizard.id].update({'ddt_next_number': ddt_number})
    #     return res

    def _get_existing_ddt(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        description = []
        picking_obj = self.pool['stock.picking']
        sequence_recovery_obj = self.pool['ir.sequence_recovery']
        picking = picking_obj.browse(cr, uid, context.get('active_ids', []), context=context)[0]
        for assign_ddt in self.browse(cr, uid, ids, context=context):
            sequence_id = picking.stock_journal_id.ddt_sequence and \
                          picking.stock_journal_id.ddt_sequence.id or False
            if not sequence_id:
                sequence_id = self.pool['ir.sequence'].search(cr, uid, [('code', '=', 'stock.ddt')])[0]
            sequence_recovery_ids = sequence_recovery_obj.search(cr, uid, [('sequence_id', '=', sequence_id)], context=context)
            for sequence_recovery in sequence_recovery_obj.browse(cr, uid, sequence_recovery_ids, context):
                description.append(sequence_recovery.name)

            result[assign_ddt.id] = '\n'.join(description)
        return result

    _columns = {
        'number_method': fields.selection([('force', 'Force'), ('sequence', 'Sequence')], 'Number Method',
                                          required=True),
        'ddt_number': fields.char('DDT', size=64, help="Keep empty for use sequence"),
        'ddt_number_already_exist': fields.boolean('DDT Number Exist'),
        'ddt_next_number': fields.char('DDT next Number', size=64),
        'ddt_date': fields.date('DDT date'),
        'existing_ddt': fields.text('DDT Existing', help="If want to recovery this number "),
        'ddt_to_recovery': fields.boolean('DDT to Recovery'),
    }

    _defaults = {
        'ddt_date': fields.date.context_today,
        'number_method': 'sequence'
        # 'ddt_next_number': _next_ddt,
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        """
        result = super(wizard_assign_ddt, self).default_get(cr, uid, fields, context=context)
        result.update({'ddt_to_recovery': False})

        if context and 'active_ids' in context and context['active_ids']:
            description = []
            picking_obj = self.pool['stock.picking']
            sequence_recovery_obj = self.pool['ir.sequence_recovery']
            picking = picking_obj.browse(cr, uid, context.get('active_ids', []), context=context)[0]

            sequence_id = picking.stock_journal_id.ddt_sequence and \
                              picking.stock_journal_id.ddt_sequence.id or False
            if not sequence_id:
                sequence_id = self.pool['ir.sequence'].search(cr, uid, [('code', '=', 'stock.ddt')])[0]
            sequence_recovery_ids = sequence_recovery_obj.search(cr, uid, [('sequence_id', '=', sequence_id)],
                                                                     context=context)
            for sequence_recovery in sequence_recovery_obj.browse(cr, uid, sequence_recovery_ids, context):
                date_recovery = sequence_recovery.date
                description.append(_('{name} of {date}').format(name=sequence_recovery.sequence, date=date_recovery))
                result.update({'ddt_to_recovery': True,
                               'number_method': 'sequence'})
            if description:
                description.append(_('For Recovery use Automatic Sequence'))

            result['existing_ddt'] = '\n'.join(description)
        return result

    def assign_ddt(self, cr, uid, ids, context=None):

        picking_obj = self.pool['stock.picking']
        for picking in picking_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            vals = {}
            if picking.ddt_number:
                raise orm.except_orm('Error', _('DTT number already assigned'))

            ddt_number = self.browse(cr, uid, ids, context=context)[0].ddt_number
            if ddt_number:
                text = _(u'{picking} has been forced DDT to {ddt_number}').format(picking=picking.name,
                                                                                  ddt_number=ddt_number)
            else:
                # Assign ddt from journal's sequence
                if picking.stock_journal_id.ddt_sequence:
                    ddt_number = self.pool['ir.sequence'].next_by_id(cr, uid, picking.stock_journal_id.ddt_sequence.id)
                else:
                    ddt_number = self.pool['ir.sequence'].get(cr, uid, 'stock.ddt')
                text = _(u'{picking} using sequence for DDT to {ddt_number}').format(picking=picking.name,
                                                                                     ddt_number=ddt_number)

            picking_obj.log(cr, uid, picking.id, text)
            picking_obj.message_append(cr, uid, [picking.id], text, body_text=text, context=context)

            recovery_ids = self.pool['ir.sequence_recovery'].search(cr, uid, [('name', '=', 'stock.picking'), ('sequence', '=', ddt_number)], context=context)

            if recovery_ids:
                recovery_id = recovery_ids[0]
                self.pool['ir.sequence_recovery'].write(cr, uid, recovery_id, {'active': False}, context)

            vals.update({
                'ddt_number': ddt_number,
                'ddt_date': self.browse(cr, uid, ids, context=context)[0].ddt_date or time.strftime(
                    DEFAULT_SERVER_DATE_FORMAT),
            })
            picking.write(vals)

        if context.get('old_result', False):
            return context['old_result']
        else:
            return {
                'type': 'ir.actions.act_window_close',
            }

    def onchange_ddt_number(self, cr, uid, ids, ddt_number, context=None):
        ddt_number_already_exist = False
        if ddt_number:
            if self.pool['stock.picking'].search(cr, SUPERUSER_ID, [('ddt_number', '=', ddt_number)], context=context):
                ddt_number_already_exist = True
        return {'value': {'ddt_number_already_exist': ddt_number_already_exist}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
