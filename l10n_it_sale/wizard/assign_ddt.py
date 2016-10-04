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

    _columns = {
        'number_method': fields.selection([('force', 'Force'), ('sequence', 'Sequence')], 'Number Method', required=True),
        'ddt_number': fields.char('DDT', size=64, help="Keep empty for use sequence"),
        'ddt_next_number': fields.char('DDT next Number', size=64),
        'ddt_date': fields.date('DDT date'),
    }

    _defaults = {
        'ddt_date': fields.date.context_today,
        'number_method': 'sequence'
        # 'ddt_next_number': _next_ddt,
    }

    def assign_ddt(self, cr, uid, ids, context=None):

        picking_obj = self.pool['stock.picking']
        for picking in picking_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            vals = {}
            if picking.ddt_number:
                raise orm.except_orm('Error', _('DTT number already assigned'))

            ddt_number = self.browse(cr, uid, ids, context=context)[0].ddt_number
            if ddt_number:
                text = _(u'{picking} has been forced DDT to {ddt_number}').format(picking=picking.name, ddt_number=ddt_number)
            else:
                # Assign ddt from journal's sequence
                if picking.stock_journal_id.ddt_sequence:
                    ddt_number = self.pool['ir.sequence'].next_by_id(cr, uid, picking.stock_journal_id.ddt_sequence.id)
                else:
                    ddt_number = self.pool['ir.sequence'].get(cr, uid, 'stock.ddt')
                text = _(u'{picking} using sequence for DDT to {ddt_number}').format(picking=picking.name, ddt_number=ddt_number)

            picking_obj.log(cr, uid, picking.id, text)
            picking_obj.message_append(cr, uid, [picking.id], text, body_text=text, context=context)

            vals.update({
                'ddt_number': ddt_number,
                'ddt_date': self.browse(cr, uid, ids, context=context)[0].ddt_date or time.strftime(DEFAULT_SERVER_DATE_FORMAT),
            })
            picking.write(vals)

        if context.get('old_result', False):
            return context['old_result']
        else:
            return {
                'type': 'ir.actions.act_window_close',
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
