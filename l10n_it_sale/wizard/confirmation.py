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
import decimal_precision as dp
import netsvc
from tools import ustr


class sale_order_confirm(orm.TransientModel):
    _inherit = "sale.order.confirm"

    _columns = {
        'cig': fields.char('CIG', size=64, help="Codice identificativo di gara"),
        'cup': fields.char('CUP', size=64, help="Codice unico di Progetto")
    }
    
    # def default_get(self, cr, uid, fields, context=None):
    #     sale_order_obj = self.pool['sale.order']
    #     if context is None:
    #         context = {}
    #
    #     res = super(sale_order_confirm, self).default_get(cr, uid, fields, context=context)
    #     sale_order_data = sale_order_obj.browse(cr, uid, context['active_ids'][0], context)
    #
    #     res['cup'] = sale_order_data.cig
    #     res['cig'] = sale_order_data.cup
    #
    #     return res
    
    def sale_order_confirmated(self, cr, uid, ids, context=None):

        sale_order_obj = self.pool['sale.order']
        result = super(sale_order_confirm, self).sale_order_confirmated(cr, uid, ids, context=context)
        sale_order_confirm_data = self.browse(cr, uid, ids[0], context=context)

        if result.get('res_id'):
            sale_order_obj.write(cr, uid, result['res_id'], {
                'cig': sale_order_confirm_data.cig,
                'cup': sale_order_confirm_data.cup,
            }, context=context)
        else:
            sale_order_obj.write(cr, uid, context['active_ids'][0], {
                'cig': sale_order_confirm_data.cig,
                'cup': sale_order_confirm_data.cup,
            }, context=context)

        for order in sale_order_obj.browse(cr, uid, [result.get('res_id') or context['active_ids'][0]], context=context):
            # partner = self.pool['res.partner'].browse(cr, uid, order.partner_id.id)
            picking_obj = self.pool['stock.picking']
            picking_ids = picking_obj.search(cr, uid, [('sale_id', '=', order.id)], context=context)
            for picking_id in picking_ids:
                picking_obj.write(cr, uid, picking_id, {
                    'cig': sale_order_confirm_data.cig or '',
                    'cup': sale_order_confirm_data.cup or ''
                }, context=context)

        return result
