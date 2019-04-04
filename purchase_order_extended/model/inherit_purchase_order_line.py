# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2017 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import orm, fields


class purchase_order_line(orm.Model):

    _inherit = 'purchase.order.line'

    def _get_order_line_sequence(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for line in self.browse(cr, uid, ids, context):
            if line.order_id:
                result[line.id] = line.order_id.order_line.index(line) + 1
            else:
                result[line.id] = 0
        return result

    # def _get_purchase_line_date(self, cr, uid, ids, context=None):
    #     result = {}
    #     for line_id in self.pool['purchase.order.line'].search(cr, uid, [('order_id', 'in', ids)], context=context):
    #         result[line_id] = True
    #     return result.keys()

    _columns = {
        'seq': fields.function(_get_order_line_sequence, string='Line #', type='integer', method=True),
        'sequence': fields.integer('Sequence',
                                   help="Gives the sequence order when displaying a list of sales order lines."),
        'date_order': fields.related('order_id', 'date_order', type='date', string='Order Date', readonly=True, store=False)
    }

    _order = 'sequence asc, id'

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(purchase_order_line, self).default_get(cr, uid, fields, context)

        if 'order_id' in context and context['order_id']:
            order = self.pool['purchase.order'].browse(cr, uid, context['order_id'], context)
            res['sequence'] = (len(order.order_line) + 1) * 10

        return res
