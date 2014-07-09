# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Didotech (<http://www.didotech.com>)
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
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
import netsvc
LOGGER = netsvc.Logger()


class repair_set_origin(orm.TransientModel):
    _name = 'repair.set.origin'
    _description = 'Set origin and date of the product to repair'

    _columns = {
        'origin': fields.char("Origin", size=256, required=True),
        'date': fields.datetime("Create Date"),
    }

    def set_origin(self, cr, uid, ids, context=None):
        origin = self.browse(cr, uid, ids, context=context)[0].origin
        date = self.browse(cr, uid, ids, context=context)[0].date

        repair_order_obj = self.pool['repair.order']

        #repair_order_obj.action_confirm(cr, uid, context['active_ids'], ())
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'repair.order', context['active_id'], 'repair_confirm', cr)
        repair_order = repair_order_obj.browse(cr, uid, context['active_id'])
        in_picking_id = repair_order.in_picking_id.id
        self.pool['stock.picking'].write(cr, uid, in_picking_id, {'origin': origin, 'date': date})
        return {'type': 'ir.actions.act_window_close'}
