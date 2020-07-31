# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp.addons.sale_subscriptions.models.sale_order import ORDER_DURATION


class SaleChangeSubscriptions(orm.TransientModel):
    _name = 'sale.change.subscriptions'
    _description = 'Change Subscriptions Duration'
    _columns = {
        'order_duration': fields.selection(ORDER_DURATION,
                                           'Subscription Duration',
                                           help='Subscription duration in days',
                                           readonly=False),
    }

    def change_subscriptions(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        order_obj = self.pool['sale.order']
        order_obj_line = self.pool['sale.order.line']

        data = self.browse(cr, uid, ids, context=context)[0]
        order_duration = data.order_duration
        sale_order = order_obj.browse(cr, uid, context['active_id'], context=context)
        order_obj.write(cr, uid, [sale_order.id], {'order_duration': order_duration}, context=context)
        for line in sale_order.order_line:
            unit_price = order_obj_line.browse(cr, uid, line.id, context).price_unit
            order_obj_line.write(cr, uid, [line.id], {'price_unit': unit_price}, context=context)
        return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
