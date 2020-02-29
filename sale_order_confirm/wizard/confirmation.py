# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2015 Didotech SRL (info at didotech.com)
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

import decimal_precision as dp
import netsvc
from openerp.osv import orm, fields
from openerp.tools.translate import _
from tools import ustr


class sale_order_confirm_line(orm.TransientModel):

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        context = context or self.pool['res.users'].context_get(cr, uid)
        for line in self.browse(cr, uid, ids, context=context):
            price_subtotal = self.calc_price_subtotal(line['quantity'], line['discount'], line['price_unit'])
            res[line['id']] = price_subtotal
        return res

    def action_add(self, cr, uid, ids, context):
        # import pdb; pdb.set_trace()
        line = self.pool['sale.order.confirm.line'].browse(cr, uid, ids, context)[0]
        line.write({
            'quantity': line.quantity + 1,
            'changed': True
        })
        return True

    def action_remove(self, cr, uid, ids, context):
        # import pdb; pdb.set_trace()
        line = self.pool['sale.order.confirm.line'].browse(cr, uid, ids, context)[0]
        if line.quantity >= 1.0:
            line.write({
                'quantity': line.quantity - 1,
                'changed': True
            })
        return True

    _name = "sale.order.confirm.line"
    _rec_name = 'product_id'
    _columns = {
        'order_id': fields.integer(_('Order Reference')),
        'sale_line_id': fields.many2one('sale.order.line', 'Order Line Reference'),
        'product_id': fields.many2one('product.product', string='Product', ondelete='CASCADE'),
        'name': fields.char('Description', size=256, select=True, readonly=True),
        'sequence': fields.integer('Sequence'),
        'price_unit': fields.float('Unit Price', digits_compute=dp.get_precision('Sale Price')),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Sale Price')),
        'quantity': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', ondelete='CASCADE'),
        'discount': fields.float('Discount (%)', digits=(16, 2)),
        'wizard_id': fields.many2one('sale.order.confirm', string="Wizard", ondelete='CASCADE'),
        'changed': fields.boolean('Changed'),
        'tax_id': fields.many2many('account.tax', string='Taxes')
    }
    _order = 'sequence, id'
    _defaults = {
        'quantity': 1.0,
        'discount': 0.0
    }

    def onchange_product(self, cr, uid, ids, product_id, product_qty, sale_order_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        
        sale_order = self.pool['sale.order'].browse(cr, uid, sale_order_id, context=context)
        product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
        result = {}
        if product_id:
            if product.default_code:
                result = {
                    'name': u'[{default_code}] {name}'.format(default_code=product.default_code, name=product.name)
                }
            else:
                result = {
                    'name': u'{name}'.format(name=product.name)
                }

            if sale_order.pricelist_id:
                result['price_unit'] = self.pool['product.pricelist'].price_get(cr, uid, [sale_order.pricelist_id.id],
                                                                                product_id, product_qty or 1.0, sale_order.partner_id.id,
                                                                                dict(
                                                                                    context,
                                                                                    uom=product.uom_id.id,
                                                                                    date=sale_order.date_order,
                                                                                ))[sale_order.pricelist_id.id]
            else:
                result['price_unit'] = product.list_price or 0.0

            result.update({
                'product_uom': product.uom_id.id,
                'changed': True,
                'discount': 0,
                'tax_id': [(6, 0, [tax_id.id for tax_id in product.taxes_id])],
            })
        
        return {'value': result}

    def onchange_qty(self, cr, uid, ids, product_id, product_qty, discount, price_unit, sale_order_id, context):
        result = {}
        sale_order = self.pool['sale.order'].browse(cr, uid, sale_order_id, context=context)
        product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
        
        if product_id and sale_order.pricelist_id:
            result.update({'price_unit': self.pool['product.pricelist'].price_get(cr, uid, [sale_order.pricelist_id.id],
                                                                            product_id, product_qty or 1.0, sale_order.partner_id.id,
                                                                            dict(
                                                                                context,
                                                                                uom=product.uom_id.id,
                                                                                date=sale_order.date_order,
                                                                            ))[sale_order.pricelist_id.id]})
        price_unit = result.get('price_unit') or 0.0
        result.update({
            'price_subtotal': self.calc_price_subtotal(product_qty, discount, price_unit),
            'changed': True
        })
        return {'value': result}

    def onchange_discount(self, cr, uid, ids, quantity, discount, price_unit):
        result = {
            'price_subtotal': self.calc_price_subtotal(quantity, discount, price_unit),
            'changed': True
        }
        return {'value': result}

    def onchange_price(self, cr, uid, ids, quantity, discount, price_unit):
        result = {
            'price_subtotal': self.calc_price_subtotal(quantity, discount, price_unit),
            'changed': True
        }
        return {'value': result}
    
    def calc_price_subtotal(self, quantity, discount, price_unit):
        products_price = price_unit * quantity
        discount_price = (discount or 0.0) * products_price / 100
        price_subtotal = products_price - discount_price
        return price_subtotal


class sale_order_confirm(orm.TransientModel):
    _name = "sale.order.confirm"
    _description = "Confirm wizard for Sale order"

    _columns = {
        'client_order_ref': fields.char('Customer Reference', size=64),
        'partner_shipping_id': fields.many2one('res.partner.address', 'Shipping Address', required=True, help="Shipping address for current sales order."),
        'order_date': fields.date('Date'),
        'sale_order_id': fields.integer('Order'),
        'new_sale_order': fields.boolean('New Sale Order'),
        'confirm_line': fields.one2many('sale.order.confirm.line', 'wizard_id', 'Products'),
        'confirm_line_qty': fields.integer('Confirm line qty')
    }
    
    def get_generic_product(self, cr, uid, context):
        product_name = _('Generic product')
        product_ids = self.pool['product.template'].search(cr, uid, [('name', '=', product_name)], context=context)
        if product_ids:
            return product_ids[0]
        else:
            uom_id = 1
            price = 1.0
            return self.pool['product.product'].create(cr, uid, {
                'name': product_name,
                'uom_id': uom_id,
                'uom_po_id': uom_id,
                'cost_price': price,
            }, context)

    def get_sale_order_confirm_line_vals(self, cr, uid, sale_order_line, context=None):
        return {
            'sequence': sale_order_line.sequence,
            'price_unit': sale_order_line.price_unit,
            'quantity': sale_order_line.product_uom_qty,
            'product_uom': sale_order_line.product_uom.id,
            'discount': sale_order_line.discount,
        }

    def default_get(self, cr, uid, fields, context=None):
        sale_order_obj = self.pool['sale.order']
        sale_order_line_obj = self.pool['sale.order.line']
        # sale_order_confirm_line_obj = self.pool['sale.order.confirm.line')
        
        context = context or self.pool['res.users'].context_get(cr, uid)
            
        res = super(sale_order_confirm, self).default_get(cr, uid, fields, context)

        sale_order = sale_order_obj.browse(cr, uid, context['active_ids'][0], context)

        res.update({
            'partner_shipping_id': sale_order.partner_shipping_id.id,
            'order_date': sale_order.date_order,
            'sale_order_id': sale_order.id,
            # 'pricelist_id': sale_order.pricelist_id.id,
            # 'partner_id': sale_order.partner_id.id,
            'client_order_ref': sale_order.client_order_ref,
            'new_sale_order': False,
            'cup': getattr(sale_order, 'cup', False),
            'cig': getattr(sale_order, 'cig', False)
        })
        sale_order_confirm_line_list = []

        for sale_order_line in sale_order.order_line:
            products_price = sale_order_line.price_unit * sale_order_line.product_uom_qty
            discount_price = (sale_order_line.discount or 0.0) * products_price / 100
            
            if sale_order_line.product_id:
                product_id = sale_order_line.product_id.id
            else:
                product_id = self.get_generic_product(cr, uid, context)
                sale_order_line_obj.write(cr, uid, sale_order_line.id, {'product_id': product_id}, context)
                
            if sale_order_line.tax_id:
                tax_id = [(6, 0, [tax_id.id for tax_id in sale_order_line.tax_id])]
            else:
                product = self.pool['product.product'].browse(cr, uid, product_id, context)
                tax_id = [(6, 0, [tax_id.id for tax_id in product.taxes_id])]
                sale_order_line_obj.write(cr, uid, sale_order_line.id, {'tax_id': tax_id}, context)

            sale_order_confirm_line_vals = {
                'order_id': sale_order.id,
                'product_id': product_id,
                'sale_line_id': sale_order_line.id,
                'name': sale_order_line.name,
                'changed': False,
                'tax_id': tax_id,
                'price_subtotal': products_price - discount_price
            }
            sale_order_confirm_line_vals.update(self.get_sale_order_confirm_line_vals(cr, uid, sale_order_line, context))
            
            sale_order_confirm_line_list.append(sale_order_confirm_line_vals)

        res['confirm_line_qty'] = len(sale_order_confirm_line_list)
        res.update(confirm_line=sale_order_confirm_line_list)
        return res
    
    def onchange_line(self, cr, uid, ids, confirm_lines):
        result = {
            'new_sale_order': False,
        }

        for confirm_line in confirm_lines:
            if (isinstance(confirm_line[2], dict)) and ('changed' in confirm_line[2]) and (confirm_line[2]['changed']):
                result['new_sale_order'] = True
            elif confirm_line[0] == 2:
                result['new_sale_order'] = True

        return {'value': result}

    def get_sale_order_line_vals(self, cr, uid, order_id, sale_order_line_data, context):
        if sale_order_line_data.product_uom:
            product_uom = sale_order_line_data.product_uom.id
        else:
            product_uom = False

        tax_ids = [tax.id for tax in sale_order_line_data.tax_id]

        return {
            'product_id': sale_order_line_data.product_id.id,
            'name': sale_order_line_data.name or sale_order_line_data.product_id.name_get()[0][1],
            'product_uom_qty': sale_order_line_data.quantity,
            'product_uom': product_uom,
            'price_unit': sale_order_line_data.price_unit,
            'discount': sale_order_line_data.discount,
            'sequence': sale_order_line_data.sequence,
            'order_id': int(order_id),
            'delay': sale_order_line_data.product_id.sale_delay,
            'tax_id': [(6, 0, tax_ids)],
            'sale_line_copy_id': sale_order_line_data.sale_line_id.id or None
        }

    def sale_order_confirmated(self, cr, uid, ids, context=None):
        sale_order_obj = self.pool['sale.order']
        sale_order_line_obj = self.pool['sale.order.line']
        sale_order_confirm_line_obj = self.pool['sale.order.confirm.line']
        wf_service = netsvc.LocalService("workflow")
        
        sale_order_confirm_data = self.read(cr, uid, ids[0], [
            'order_date',
            'sale_order_id',
            'new_sale_order',
            'confirm_line',
            'client_order_ref',
            'order_date',
            'partner_shipping_id',
            'confirm_line_qty'
        ], context)
        new_order_id = False

        if sale_order_confirm_data['new_sale_order'] or not sale_order_confirm_data['confirm_line_qty'] == len(sale_order_confirm_data['confirm_line']):
            old_sale_order_data = sale_order_obj.read(cr, uid, sale_order_confirm_data['sale_order_id'], ['shop_id', 'partner_id', 'partner_order_id', 'partner_invoice_id', 'pricelist_id', 'sale_version_id', 'version', 'name', 'order_policy', 'picking_policy', 'invoice_quantity', 'section_id', 'categ_id'], context)
            new_sale_order = {}
            for key in ('shop_id', 'partner_id', 'partner_order_id', 'partner_invoice_id', 'pricelist_id', 'contact_id'):
                new_sale_order[key] = old_sale_order_data.get(key, False) and old_sale_order_data[key][0] or False
            for key in ('picking_policy', 'order_policy', 'invoice_quantity'):
                new_sale_order[key] = old_sale_order_data.get(key, False)
            
            if not old_sale_order_data['sale_version_id']:
                old_sale_order_name = old_sale_order_data['name'] + u" V.2"
                old_sale_order_data['version'] = 2
                new_sale_order['sale_version_id'] = old_sale_order_data['id']
            else:
                old_sale_order_name = old_sale_order_data['name'].split('V')[0] + u"V." + ustr(old_sale_order_data['version'] + 1)
                new_sale_order['sale_version_id'] = old_sale_order_data['sale_version_id'][0]
            
            new_sale_order.update({
                'version': old_sale_order_data['version'] + 1,
                'name': old_sale_order_name,
                'client_order_ref': sale_order_confirm_data['client_order_ref'],
                'date_confirm': sale_order_confirm_data['order_date'],
                'partner_shipping_id': sale_order_confirm_data['partner_shipping_id'][0]
            })
            # qui creo il nuovo sale.order
            context['versioning'] = True
            new_order_id = sale_order_obj.create(cr, uid, new_sale_order, context=context)

            # sequence = 10
            for sale_order_confirm_line_data in sale_order_confirm_line_obj.browse(cr, uid, sale_order_confirm_data['confirm_line'], context):
                sale_order_line_vals = self.get_sale_order_line_vals(cr, uid, new_order_id, sale_order_confirm_line_data, context)
                sale_order_line_obj.create(cr, uid, sale_order_line_vals, context=context)

            wf_service.trg_validate(uid, 'sale.order', new_order_id, 'order_confirm', cr)
            # wf_service.trg_validate(uid, 'sale.order', sale_order_confirm_data['sale_order_id'], 'cancel', cr)
            sale_order_obj.write(cr, uid, sale_order_confirm_data['sale_order_id'], {'active': False}, context)

            view_ids = self.pool['ir.model.data'].get_object_reference(cr, uid, 'sale', 'view_order_form')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Sale Order',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_ids and view_ids[1] or False,
                'res_model': 'sale.order',
                'nodestroy': True,
                'target': 'current',
                'res_id': new_order_id,
            }
        else:
            sale_order_obj.write(cr, uid, sale_order_confirm_data['sale_order_id'], {
                'customer_validation': True,
                'client_order_ref': sale_order_confirm_data['client_order_ref'],
                'partner_shipping_id': sale_order_confirm_data['partner_shipping_id'][0]
            }, context)

            wf_service.trg_validate(uid, 'sale.order', sale_order_confirm_data['sale_order_id'], 'order_confirm', cr)
            # need to write after validation
            sale_order_obj.write(cr, uid, sale_order_confirm_data['sale_order_id'], {
                'date_confirm': sale_order_confirm_data['order_date'],
            }, context)
            return {
                'type': 'ir.actions.act_window_close'
            }
