# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>).
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
from tools import ustr
from tools.translate import _


class stock_picking(orm.Model):

    _inherit = "stock.picking"

    _columns = {
        'product_barcode': fields.char('Barcode', readonly=True, states={'draft': [('readonly', False)]}),
    }

    def onchange_product_barcode(self, cr, uid, ids, product_barcode, address_id, picking_type, stock_journal_id, move_lines, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context.update({
            'address_out_id': address_id,
            'picking_type': picking_type,
            'stock_journal_id': stock_journal_id
        })
        warning = {}
        stock_move_obj = self.pool['stock.move']
        product_obj = self.pool['product.product']
        product_ids = product_obj.search(cr, uid, [('ean13', '=', product_barcode)], context=context)
        if not product_ids:
            product_ids = product_obj.search(cr, uid, [('default_code', '=', product_barcode)], context=context)
        if not product_ids:
            product_ids = product_obj.search(cr, uid, [('name', '=', product_barcode)], context=context)
        if product_ids:
            find_line = False
            product_id = product_ids[0]
            for line in move_lines:
                # create new line
                if line[0] == 0 or line[0] == 1:  # new or update
                    # (0, 0,  { values })    link to a new record that needs to be created with the given values dictionary
                    # (1, ID, { values })    update the linked record with id = ID (write *values* on it)
                    if 'product_id' in line[2] and line[2]['product_id'] == product_id:
                        product_qty = line[2]['product_qty'] + 1
                        product_change_value = stock_move_obj.onchange_product_id(cr, uid, ids, product_id, line[2]['location_id'], line[2]['location_dest_id'], address_id)
                        warning = product_change_value.get('warning')
                        line[2].update(product_change_value.get('value'))
                        line[2].update({'product_id': product_id,
                                        'product_qty': product_qty})
                        find_line = True
                        continue
                elif line[0] == 4 and line[1]:
                    stock_move = stock_move_obj.browse(cr, uid, line[1], context)
                    if stock_move.product_id.id == product_id:
                        line[0] = 1  # update
                        line[2] = {'product_qty': stock_move.product_qty + 1,
                                   'product_id': product_id}
                        # (1, ID, { values })    update the linked record with id = ID (write *values* on it)
                        find_line = True
                        continue
            # if not find product need to create line
            if not find_line:
                line_values = stock_move_obj.default_get(cr, uid, ['location_id', 'location_dest_id', 'price_unit', 'note', 'date', 'prodlot_id'], context=context)
                product_qty = 1
                try:
                    product_change_value = stock_move_obj.onchange_product_id(cr, uid, ids, product_id, line_values['location_id'], line_values['location_dest_id'], address_id)
                    warning = product_change_value.get('warning')
                except Exception, e:  # if not set customer
                    return {'value': {
                        'order_line': move_lines,
                        'product_barcode': False
                    }, 'warning': {
                        'title': e[0],
                        'message': e[1],
                    }}
                line_values.update(product_change_value.get('value'))
                product_change_value = stock_move_obj.onchange_quantity(cr, uid, ids, product_id, product_qty, line_values['product_uom'], line_values['product_uos'])
                line_values.update(product_change_value.get('value'))
                line_values.update({'product_id': product_id,
                                    'product_qty': product_qty})
                if 'name' not in line_values:
                    line_values.update(
                        {
                            'name': self.pool['product.product'].browse(cr, uid, product_id, context).name
                        }
                    )
                move_lines.append([0, False, line_values])
        else:
            title = _('Error')
            message = _('Not able to find product with code {code}').format(code=product_barcode)
            warning = {
                'title': title,
                'message': message,
            }

        return {'value': {
            'move_lines': move_lines,
            'product_barcode': False
        }, 'warning': warning}
