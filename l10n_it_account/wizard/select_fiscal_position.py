# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Andrei Levin (andrei.levin at didotech.com)
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

from openerp.osv import fields, orm


class select_fiscal_position(orm.TransientModel):
    _name = "select.fiscal.position"
    _description = "Select Fiscal Position"
    _inherit = "ir.wizard.screen"
    
    def _get_accounts(self, cr, uid, context=None):
        fiscal_position_obj = self.pool['account.fiscal.position']
        partner_id = context.get('active_id', False)
        if partner_id:
            fiscal_position_ids = fiscal_position_obj.search(cr, uid, ['|', ('partner_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        else:
            fiscal_position_ids = fiscal_position_obj.search(cr, uid, [('partner_id', '=', False)], context=context)
        
        result = []
        
        for fiscal_position in fiscal_position_obj.browse(cr, uid, fiscal_position_ids, context):
            result.append((fiscal_position.id, fiscal_position.name))
        return result
    
    _columns = {
        'partner_id': fields.integer('Partner ID'),
        'property_account_position': fields.selection(_get_accounts, 'Fiscal Position', required=False),
    }

    def action_select_position(self, cr, uid, ids, context):
        selected_position = self.browse(cr, uid, ids[0], context=context)
        self.pool['res.partner'].write(cr, uid, selected_position.partner_id, {'property_account_position': u'account.fiscal.position,' + selected_position.property_account_position})
        return {'type': 'ir.actions.act_window_close'}
