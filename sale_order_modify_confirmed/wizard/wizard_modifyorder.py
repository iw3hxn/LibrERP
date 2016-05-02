# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Andre@ (<a.gallina@cgsoftware.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from tools.translate import _
import decimal_precision as dp


class wizard_modifyorder(orm.TransientModel):

    _name = "wizard.modifyorder"

    _columns = {
        'order_id': fields.many2one('sale.order', 'Sale Order'),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'partner_invoice_id': fields.many2one(
            'res.partner.address', 'Invoice Address'),
        'partner_shipping_id': fields.many2one(
            'res.partner.address', 'Delivery Address'),
        'order_line': fields.one2many(
            'wizard.order.line', 'order_id', 'Order Lines'),
    }

    def view_init(self, cr, uid, fields_list, context=None):
        res = super(wizard_modifyorder, self).view_init(
            cr, uid, fields_list, context)
        select_order = context['active_ids']
        if len(select_order) > 1:
            raise orm.except_orm(
                _('Errore'),
                _('Select only one Order to modify!'))
        return res

    def default_get(self, cr, uid, fields, context=None):
        if context:
            order_id = context.get('active_id')
            order = self.pool.get('sale.order').browse(
                cr, uid, order_id, context)
            line_value = []
            for line in order.order_line:
                if line.product_id and line.product_id.type != 'service':
                    line_value.append({
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'line_id': line.id,
                        'purchase_price': line.purchase_price,
                    })
            return {
                'order_id': order.id,
                'partner_id': order.partner_id.id,
                'partner_invoice_id': order.partner_invoice_id.id,
                'partner_shipping_id': order.partner_shipping_id.id,
                'order_line': line_value,
            }

    def write_order(self, cr, uid, ids, context=None):
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)

        wizard = self.browse(cr, uid, ids, context)[0]

        for line in wizard.order_line:
            line.line_id.write({
                'name': line.name,
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'purchase_price': line.purchase_price,
            })
            for move in line.line_id.move_ids:
                if move.state != 'done':
                    move.write({
                        'product_id': line.product_id.id,
                    })
                elif move.product_id != line.product_id:
                    raise orm.except_orm(
                        _('Errore'),
                        _('Impossible to change product {product} because just delivery with picking {picking}!'.format(
                            product=line.product_id.name, picking=move.picking_id.name_get()[0][1])))

        if wizard.order_id.picking_ids:
            order = wizard.order_id

            for picking in order.picking_ids:
                if picking.address_delivery_id.id != wizard.partner_shipping_id.id:
                    picking.write({
                        'address_delivery_id': wizard.partner_shipping_id.id
                    })
        wizard.order_id.write({
            'partner_invoice_id': wizard.partner_invoice_id.id,
            'partner_shipping_id': wizard.partner_shipping_id.id,
        })

        return {'type': 'ir.actions.act_window_close'}

    def onchange_order_id(self, cr, uid, ids, order_id, context=None):
        if not order_id:
            return {}
        order = self.pool.get('sale.order').browse(
            cr, uid, order_id, context)
        line_value = []
        for line in order.order_line:
            if line.product_id and line.product_id.type != 'service':
                line_value.append({
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'line_id': line.id,
                    'purchase_price': line.purchase_price,
                })

        res_value = {
            'order_id': order.id,
            'partner_id': order.partner_id.id,
            'partner_invoice_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'order_line': line_value,
        }

        return {'value': res_value}


class wizard_order_line(orm.TransientModel):

    _name = "wizard.order.line"

    _columns = {
        'order_id': fields.many2one(
            'wizard.modifyorder', 'Order Reference'),
        'line_id': fields.many2one(
            'sale.order.line', 'Line id'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('type', '!=', 'service')]),
        'name': fields.char('Description', size=64),
        'price_unit': fields.float('Unit Price', digits_compute=dp.get_precision('Product Price')),
        'discount': fields.float('Discount (%)', digits_compute=dp.get_precision('Discount')),
        'purchase_price': fields.float('Purchase Price', digits_compute=dp.get_precision('Product Price')),
    }
