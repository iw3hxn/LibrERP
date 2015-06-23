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

    _columns = {
        'ddt_number': fields.char('DDT', size=64),
        'ddt_next_number': fields.char('DDT next Number', size=64),
        'ddt_date': fields.date('DDT date'),
    }

    _defaults = {
        'ddt_date': fields.date.context_today,
        # 'ddt_next_number': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').current_number(cr, uid, 38),
    }

    def assign_ddt(self, cr, uid, ids, context=None):
        picking_obj = self.pool['stock.picking']
        for picking in picking_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            vals = {}
            if picking.ddt_number:
                raise orm.except_orm('Error', _('DTT number already assigned'))
            if not self.browse(cr, uid, ids, context=context)[0].ddt_number:
            # Assign ddt from journal's sequence
                if picking.stock_journal_id.ddt_sequence:
                    vals['ddt_number'] = self.pool['ir.sequence'].get(cr, uid, picking.stock_journal_id.ddt_sequence.code),

                else:
                    vals['ddt_number'] = self.pool['ir.sequence'].get(cr, uid, 'stock.ddt'),
            else:
                vals['ddt_number'] = self.browse(cr, uid, ids, context=context)[0].ddt_number
            vals['ddt_date'] = self.browse(cr, uid, ids, context=context)[0].ddt_date or time.strftime(DEFAULT_SERVER_DATE_FORMAT),

            picking.write(vals)
        return {
            'type': 'ir.actions.act_window_close',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
