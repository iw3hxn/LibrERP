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
        purchase_order_line = self.browse(cr, uid, ids, context)

        result = {}
        for line in purchase_order_line:
            if line.order_id:
                result[line.id] = line.order_id.order_line.index(line) + 1
            else:
                result[line.id] = 0
        return result

    def _get_purchase_line(self, cr, uid, ids, context=None):
        result = {}
        for purchase in self.pool['purchase.order'].browse(cr, uid, ids, context=context):
            for purchase_order_line in purchase.order_line:
                result[purchase_order_line.id] = True
        return result.keys()

    _columns = {
        'sequence': fields.function(_get_order_line_sequence, string='Line #', type='integer', method=True),
        'date_order': fields.related('order_id', 'date_order', string='Order Date', readonly=True, type="date", store={
                'purchase.order': (_get_purchase_line, ['date_order'], 10),
        },)
    }

