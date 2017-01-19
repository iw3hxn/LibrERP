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
from tools.translate import _


class stock_partial_picking(orm.TransientModel):

    _inherit = "stock.partial.picking"

    _columns = {
        'qty_barcode': fields.integer('Qty'),
        'product_barcode': fields.char('Barcode'),
    }

    _defaults = {
        'qty_barcode': 1
    }

    def onchange_product_barcode(self, cr, uid, ids, qty_barcode, product_barcode, move_ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        qty_barcode = qty_barcode or 1
        warning = {}
        partial_picking_line_obj = self.pool['stock.partial.picking.line']
        product_obj = self.pool['product.product']
        product_ids = product_obj.search(cr, uid, [('ean13', '=', product_barcode)], context=context)
        if not product_ids:
            product_ids = product_obj.search(cr, uid, [('default_code', '=', product_barcode)], context=context)
        if not product_ids:
            product_ids = product_obj.search(cr, uid, [('name', '=', product_barcode)], context=context)
        if product_ids:
            find_line = False
            product_id = product_ids[0]
            for line in move_ids:
                # create new line
                if line[0] == 0 or line[0] == 1:  # new or update
                    # (0, 0,  { values })    link to a new record that needs to be created with the given values dictionary
                    # (1, ID, { values })    update the linked record with id = ID (write *values* on it)
                    if 'product_id' in line[2] and line[2]['quantity'] == product_id:
                        quantity = line[2]['quantity'] + qty_barcode
                        line[2].update({'product_id': product_id,
                                        'quantity': quantity})
                        find_line = True
                        continue
                elif line[0] == 4 and line[1]:
                    purchase_order_line = partial_picking_line_obj.browse(cr, uid, line[1], context)
                    if purchase_order_line.product_id.id == product_id:
                        line[0] = 1  # update
                        line[2] = {'quantity': purchase_order_line.quantity + qty_barcode,
                                   'product_id': product_id}
                        # (1, ID, { values })    update the linked record with id = ID (write *values* on it)
                        find_line = True
                        continue
            # if not find product need to create line
            if not find_line:
                title = _('Error')
                message = _('The product with {code} is not on delivery').format(code=product_barcode)
                warning = {
                    'title': title,
                    'message': message,
                }
        else:
            title = _('Error')
            message = _('Not able to find product with code {code}').format(code=product_barcode)
            warning = {
                'title': title,
                'message': message,
            }

        return {'value': {
            'move_ids': move_ids,
            'product_barcode': False
        }, 'warning': warning}
