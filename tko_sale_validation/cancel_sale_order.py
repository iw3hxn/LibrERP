# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 1.3 Thinkopen Solutions, Lda. All Rights Reserved
#    http://www.thinkopensolutions.com.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version $revnoof the License, or
#    (at your option) any later version.51
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

from osv import osv, fields
import netsvc

class cancel_sale_order(osv.osv_memory):
    _name="cancel.sale.order"
    _description = "Cancel Sale Order"
    
    def cancel_sale_order_action(self, cr, uid, ids, context=None):
        sale_order = self.pool.get('sale.order')
        document = sale_order.browse(cr, uid, context['active_ids'][0])
        obj = self.browse(cr, uid, ids)
        if obj and document:
            args = {
                    'validation_observation' : obj[0].cancel_description.decode('utf-8'),
                    }
            sale_order.write(cr, uid, context['active_ids'][0], args)
            
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'sale.order', context['active_ids'][0], 'order_refuse', cr)
            
            return {'type': 'ir.actions.act_window_close'}
        else:
            return False
        
    _columns = {'cancel_description': fields.text('Description', size=128, required=True)}

cancel_sale_order()
