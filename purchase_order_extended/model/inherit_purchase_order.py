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
from openerp.tools.translate import _


class purchase_order(orm.Model):

    _inherit = 'purchase.order'

    def service_only(self, cr, uid, ids, values, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        deleted_products = []
        service = True
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        if values and 'order_line' in values and values['order_line']:
            for line in values['order_line']:
                # create new line
                if line[0] == 0:
                    if 'product_id' in line[2] and line[2]['product_id']:
                        product = self.pool['product.product'].browse(cr, uid, line[2]['product_id'], context)
                        if not product.type == 'service':
                            if line[0] == 0:
                                return False
                elif line[0] == 2 and line[1]:
                    order_line = self.pool['purchase.order.line'].browse(cr, uid, line[1], context)
                    if order_line.product_id and not order_line.product_id.type == 'service':
                        deleted_products.append(order_line.product_id.id)
        elif not ids:
            return False
        else:
            service = False

        for order in self.browse(cr, uid, ids, context):
            if order.order_line:
                for order_line in order.order_line:
                    if order_line.product_id.type != 'service' or order_line.product_id.id in deleted_products:
                        return False
            elif not service:
                    return False
        return True

    def hook_sale_state(self, cr, uid, ids, vals, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # function call if change state the purchase order
        return True

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        company = self.pool['res.users'].browse(cr, uid, uid).company_id
        if self.service_only(cr, uid, False, vals, context) and vals.get('invoice_method', '') == 'picking':
            if company.auto_order_policy:
                vals.update({'invoice_method': 'manual'})
            else:
                raise orm.except_orm(_('Warning'), _("You can't create an order with Invoicing being based on Picking if there are only service products"))
        elif self.service_only(cr, uid, False, vals, context):
                if company.auto_order_policy:
                    vals.update({'invoice_method': 'manual'})
        else:
            if company.auto_order_policy:
                default = self.default_get(cr, uid, ['invoice_method'], context)
                vals.update({'invoice_method': default.get('invoice_method', 'manual')})

        ids = super(purchase_order, self).create(cr, uid, vals, context=context)
        if vals.get('carrier_id', False) or vals.get('payment_term', False):
            if not isinstance(ids, (list, tuple)):
                order_ids = [ids]
            order = self.browse(cr, uid, order_ids, context)[0]
            partner_vals = {}
            if not order.partner_id.property_delivery_carrier:
                partner_vals['property_delivery_carrier'] = vals.get('carrier_id')
            if not order.partner_id.property_payment_term:
                partner_vals['property_payment_term'] = vals.get('payment_term')
            if partner_vals:
                self.pool['res.partner'].write(cr, uid, [order.partner_id.id], partner_vals, context)
        return ids

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        for order in self.browse(cr, uid, ids, context):
            company = self.pool['res.users'].browse(cr, uid, uid).company_id
            if self.service_only(cr, uid, [order.id], vals, context) and vals.get('invoice_method', order.invoice_method) == 'picking':
                if company.auto_order_policy:
                    vals.update({'invoice_method': 'manual'})
                else:
                    raise orm.except_orm(_('Warning'), _(
                        "You can't create an order with Invoicing being based on Picking if there are only service products"))
            elif self.service_only(cr, uid, [order.id], vals, context):
                if company.auto_order_policy:
                    vals.update({'invoice_method': 'manual'})
            else:
                if company.auto_order_policy:
                    default = self.default_get(cr, uid, ['invoice_method'], context)
                    vals.update({'invoice_method': default.get('invoice_method', 'manual')})

            # adaptative function: the system learn
            if vals.get('carrier_id', False) or vals.get('payment_term', False):
                partner_vals = {}
                if not order.partner_id.property_delivery_carrier:
                    partner_vals['property_delivery_carrier'] = vals.get('carrier_id')
                if not order.partner_id.property_payment_term:
                    partner_vals['property_payment_term'] = vals.get('payment_term')
                if partner_vals:
                    self.pool['res.partner'].write(cr, uid, [order.partner_id.id], partner_vals, context)

        if vals.get('state', False):
            self.hook_sale_state(cr, uid, ids, vals, context)

        return super(purchase_order, self).write(cr, uid, ids, vals, context=context)
