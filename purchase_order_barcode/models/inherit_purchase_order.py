# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Alejandro Núñez Liz$
#    $Omar Castiñeira Saavedra$
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
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


class purchase_order(orm.Model):
    """ Modificaciones de sale order para añadir la posibilidad de versionar el pedido de venta. """
    _inherit = "purchase.order"

    _columns = {
        'product_barcode': fields.char('Barcode', readonly=True, states={'draft': [('readonly', False)]}),
    }

    def onchange_product_barcode(self, cr, uid, ids, product_barcode, partner_id, pricelist_id, fiscal_position, order_line, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        warning = {}
        purchase_order_line_obj = self.pool['purchase.order.line']
        product_obj = self.pool['product.product']
        product_ids = product_obj.search(cr, uid, [('ean13', '=', product_barcode)], context=context)
        if not product_ids:
            product_ids = product_obj.search(cr, uid, [('default_code', '=', product_barcode)], context=context)
        if not product_ids:
            product_ids = product_obj.search(cr, uid, [('name', '=', product_barcode)], context=context)
        if product_ids:
            find_line = False
            product_id = product_ids[0]
            if not product_obj.browse(cr, uid, product_id, context).purchase_ok:
                title = _('Error')
                message = _('Not able to purchase product with code {code}').format(code=product_barcode)
                return {'value': {
                    'order_line': order_line,
                    'product_barcode': False
                }, 'warning': {
                    'title': title,
                    'message': message,
                }}
            for line in order_line:
                # create new line
                if line[0] == 0 or line[0] == 1:  # new or update
                    # (0, 0,  { values })    link to a new record that needs to be created with the given values dictionary
                    # (1, ID, { values })    update the linked record with id = ID (write *values* on it)
                    if 'product_id' in line[2] and line[2]['product_id'] == product_id:
                        product_qty = line[2]['product_qty'] + 1
                        product_change_value = purchase_order_line_obj.onchange_product_id(cr, uid, ids, pricelist_id, product_id, product_qty, False, partner_id, False, fiscal_position, False, '', False, '', context)
                        warning = product_change_value.get('warning')
                        line[2].update(product_change_value.get('value'))
                        line[2].update({'product_id': product_id,
                                        'product_qty': product_qty})
                        find_line = True
                        continue
                elif line[0] == 4 and line[1]:
                    purchase_order_line = purchase_order_line_obj.browse(cr, uid, line[1], context)
                    if purchase_order_line.product_id.id == product_id:
                        line[0] = 1  # update
                        line[2] = {'product_qty': purchase_order_line.product_qty + 1,
                                   'product_id': product_id}
                        # (1, ID, { values })    update the linked record with id = ID (write *values* on it)
                        find_line = True
                        continue
            # if not find product need to create line
            if not find_line:
                line_values = purchase_order_line_obj.default_get(cr, uid, [], context=context)
                product_qty = 1
                try:
                    product_change_value = purchase_order_line_obj.onchange_product_id(cr, uid, ids, pricelist_id, product_id, product_qty, False, partner_id, False, fiscal_position, False, '', False, '', context)
                    warning = product_change_value.get('warning')
                except Exception, e:  # if not set customer
                    return {'value': {
                        'order_line': order_line,
                        'product_barcode': False
                    }, 'warning': {
                        'title': e[0],
                        'message': e[1],
                    }}

                line_values.update(product_change_value.get('value'))
                line_values.update({'product_id': product_id,
                                    'product_qty': product_qty})
                order_line.append([0, 0, line_values])
        else:
            title = _('Error')
            message = _('Not able to find product with code {code}').format(code=product_barcode)
            warning = {
                'title': title,
                'message': message,
            }

        return {'value': {
            'order_line': order_line,
            'product_barcode': False
        }, 'warning': warning}
