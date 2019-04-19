# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

import decimal_precision as dp
from openerp.osv import orm, fields
from tools.translate import _


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
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(wizard_modifyorder, self).view_init(
            cr, uid, fields_list, context)
        select_order = context['active_ids']
        if len(select_order) > 1:
            raise orm.except_orm(
                _('Errore'),
                _('Select only one Order to modify!'))
        return res

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if context:
            order_id = context.get('active_id')
            order = self.pool.get('sale.order').browse(
                cr, uid, order_id, context)
            line_value = []
            for line in order.order_line:
                if line.product_id and line.product_id.type == 'service':
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
        context = context or self.pool['res.users'].context_get(cr, uid)

        wizard = self.browse(cr, uid, ids, context)[0]
        order = wizard.order_id
        for line in wizard.order_line:
            if line.line_id:
                line.line_id.write({
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
                            _('Impossible to change product {product} because just delivery with picking {picking}!').format(
                                product=line.product_id.name, picking=move.picking_id.name_get()[0][1]))
            else:
                sale_order_line_obj = self.pool['sale.order.line']
                line_value = sale_order_line_obj.product_id_change(cr, uid, [], order.pricelist_id.id, line.product_id.id, qty=1,
                                                                   uom=False, qty_uos=0, uos=False, name='',
                                                                   partner_id=order.partner_id.id,
                                                                   lang=False, update_tax=True, date_order=order.date_order,
                                                                   packaging=False, fiscal_position=order.fiscal_position.id, flag=False,
                                                                   context=context).get('value')
                line_value.update({
                    'product_id': line.product_id.id,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'tax_id': [(6, 0, line_value.get('tax_id'))],
                    'order_id': order.id,
                    'product_sale_order_history_ids': []
                })
                line_id = sale_order_line_obj.create(cr, uid, line_value, context)
                line.write({'line_id': line_id})
        if wizard.order_id.picking_ids:
            for picking in order.picking_ids:
                if wizard.order_id.partner_shipping_id.id != wizard.partner_shipping_id.id:
                    if hasattr(picking, 'ddt_number') and not picking.ddt_number:
                        picking.write({
                            'address_delivery_id': wizard.partner_shipping_id.id
                        })
                    else:
                        raise orm.except_orm(
                            _('Error'),
                            _('There are a just done DDT'))
        wizard.order_id.write({
            'partner_invoice_id': wizard.partner_invoice_id.id,
            'partner_shipping_id': wizard.partner_shipping_id.id,
        })

        return {'type': 'ir.actions.act_window_close'}

    def onchange_order_id(self, cr, uid, ids, order_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not order_id:
            return {}
        order = self.pool['sale.order'].browse(cr, uid, order_id, context)
        line_value = []
        for line in order.order_line:
            if line.product_id and line.product_id.type == 'service':
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
        'product_id': fields.many2one('product.product', 'Product', domain=[('type', '=', 'service')], required=1),
        'name': fields.char('Description', size=64),
        'price_unit': fields.float('Unit Price', digits_compute=dp.get_precision('Product Price')),
        'discount': fields.float('Discount (%)', digits_compute=dp.get_precision('Discount')),
        'purchase_price': fields.float('Purchase Price', digits_compute=dp.get_precision('Product Price')),
    }

    def create(self, cr, uid, values, context=None):
        if 'line_id' not in values:
            sale_order_line_obj = self.pool['sale.order.line']
            order = self.browse(cr, uid, id, context)
            pricelist = order.pricelist_id.id
            line_value = sale_order_line_obj.product_id_change(cr, uid, [], pricelist, values['product_id'], qty=1,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=context)
            line_id = sale_order_line_obj.create(cr, uid, line_value, context)
            values['line_id'] = line_id
        return super(wizard_order_line, self).create(cr, uid, values, context)
