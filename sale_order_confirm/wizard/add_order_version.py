# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2014 Didotech SRL (info at didotech.com)
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
##############################################################################
from openerp.osv import orm, fields
from openerp.tools.translate import _


class sale_order_revision_note(orm.TransientModel):
    _name = "sale.order.revision.note"
    _columns = {
        'name': fields.char('Reason', size=256, select=True),
    }
    
    def create_revision(self, cr, uid, ids, context=None):
        if not ids:
            return False
        sale_order_obj = self.pool['sale.order']
        active_ids = context.get('active_ids', [])
        if not active_ids:
            return False
        reason_note = self.browse(cr, uid, ids[0], context=context).name
        sale_order_obj.write(cr, uid, active_ids, {'revision_note': reason_note}, context=context)
        res = sale_order_obj.action_previous_version(cr, uid, active_ids, context=context)
        if reason_note:
            text = _("Create New Revision for this reason: '%s' ") % reason_note
        else:
            text = _("Create New Revision")
        sale_order_obj.message_append(cr, uid, [res['res_id']], text, body_text=text, context=context)
        return res
    
    def reject_revision(self, cr, uid, ids, context=None):
        if not ids:
            return False
        sale_order_obj = self.pool['sale.order']
        active_ids = context.get('active_ids', [])
        if not active_ids:
            return False
        reason_note = self.browse(cr, uid, ids[0], context=context).name
        sale_order_obj.write(cr, uid, active_ids, {'revision_note': reason_note}, context=context)
        if reason_note:
            text = _("Add Note for Reject: '%s' ") % reason_note
            sale_order_obj.message_append(cr, uid, active_ids, text, body_text=text, context=context)
        sale_order_obj.action_cancel(cr, uid, active_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}