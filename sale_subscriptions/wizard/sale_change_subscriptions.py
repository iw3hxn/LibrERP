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

from osv import osv, fields
from tools.translate import _

class sale_change_subscriptions(osv.osv_memory):
    _name = 'sale.change.subscriptions'
    _description = 'Change Currency'
    _columns = {
               'order_duration': fields.selection(
            [
                (30, '1 month'),
                (60, '2 months'),
                (90, '3 months'),
                (120, '4 months'),
                (180, '6 months'),
                (365, '1 year'),
                (730, '2 years'),
                (1095, '3 years'),
                (1460, '4 years'),
                (1825, '5 years')
            ],
            'Subscription Duration',
            help='Subscription duration in days',
            readonly=False),
    }

    def change_subscriptions(self, cr, uid, ids, context=None):
        tax_obj = self.pool['account.tax']
        cur_obj = self.pool['res.currency']
        order_obj = self.pool['sale.order']
        order_obj_line = self.pool.get('sale.order.line')
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        data = self.browse(cr, uid, ids, context=context)[0]
        order_duration = data.order_duration
        sale_order = order_obj.browse(cr, uid, context['active_id'], context=context)
        order_obj.write(cr, uid, [sale_order.id], {'order_duration': order_duration}, context=context)
        for line in sale_order.order_line:
            unit_price = order_obj_line.browse(cr, uid, line.id).price_unit
            order_obj_line.write(cr, uid, [line.id], {'price_unit': unit_price}, context=context)
        return {'type': 'ir.actions.act_window_close'}

sale_change_subscriptions()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
