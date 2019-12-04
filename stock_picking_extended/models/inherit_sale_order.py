# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    Copyright (C) 2013-2014
#    Didotech srl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta

import decimal_precision as dp
from dateutil.relativedelta import relativedelta
from openerp.osv import orm, fields
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from tools.translate import _


class sale_order_line(orm.Model):

    _inherit = "sale.order.line"
    _columns = {
        'purchase_price': fields.float(
            'Cost Price', digits_compute=dp.get_precision('Purchase Price')),
        'th_weight': fields.float(
            'Weight', readonly=True, states={'draft': [('readonly', False)]},
            digits_compute=dp.get_precision('Stock Weight')),
    }


class sale_order(orm.Model):

    _inherit = "sale.order"
    _columns = {
        'carriage_condition_id': fields.many2one('stock.picking.carriage_condition', 'Carriage condition'),
        'goods_description_id': fields.many2one('stock.picking.goods_description', 'Description of goods'),
        'order_policy': fields.selection([
            ('prepaid', 'Pay before delivery'),
            ('manual', 'Deliver & invoice on demand'),
            ('picking', 'Invoice based on deliveries'),
            # ('postpaid', 'Invoice on order after delivery'),# SERGIO removed for various problem of usability
            # read https://bugs.launchpad.net/openobject-addons/+bug/1160835/comments/18
        ], 'Invoice Policy'),
        'minimum_planned_date': fields.date('Expected Date', select=True),
    }

    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        if order.minimum_planned_date:
            date_planned = order.minimum_planned_date
        else:
            date_planned = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=line.delay or 0.0)
            date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return date_planned

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            partner = self.pool['res.partner'].browse(cr, uid, partner_id, context=context)
            result['value']['carriage_condition_id'] = partner.carriage_condition_id.id
            result['value']['goods_description_id'] = partner.goods_description_id.id
        return result

    def action_wait(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for order in self.browse(cr, uid, ids, context):
            if not self.service_only(cr, uid, [order], context):
                if order.company_id.required_minimum_planned_date and not order.minimum_planned_date:
                    title = _(u'Error')
                    msg = _(u'Is not possible to confirm because order {order} have no Minimum Planned Date').format(
                        order=order.name)
                    raise orm.except_orm(_(title), _(msg))

        return super(sale_order, self).action_wait(cr, uid, ids, context)

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        res = super(sale_order, self)._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context)
        company = order.company_id
        if not company.note_on_stock_move:
            if 'note' in res:
                del res['note']
        return res

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(sale_order, self)._prepare_order_picking(cr, uid, order, context)
        # if order.minimum_planned_date:
        #     res['minimum_planned_date'] = order.minimum_planned_date
        res.update({
            'address_id': order.partner_invoice_id.id,
            'address_delivery_id': order.partner_shipping_id.id,
            'carriage_condition_id': order.carriage_condition_id and order.carriage_condition_id.id or False,
            'goods_description_id': order.goods_description_id and order.goods_description_id.id or False,
            'address_delivery_id': order.partner_shipping_id.id,
        })
        return res

    # Simplify code
    # def _make_invoice(self, cr, uid, order, lines, context=None):
    #     # implementation to put advance reference in invoices
    #     inv_obj = self.pool['account.invoice']
    #     obj_invoice_line = self.pool['account.invoice.line']
    #     if context is None:
    #         context = self.pool['res.users'].context_get(cr, uid)
    #     invoiced_sale_line_ids = self.pool['sale.order.line'].search(cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)], context=context)
    #     from_line_invoice_ids = []
    #     for invoiced_sale_line_id in self.pool['sale.order.line'].browse(cr, uid, invoiced_sale_line_ids, context=context):
    #         for invoice_line_id in invoiced_sale_line_id.invoice_lines:
    #             if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
    #                 from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
    #     for preinv in order.invoice_ids:
    #         if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
    #             for preline in preinv.invoice_line:
    #                 inv_line_id = obj_invoice_line.copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit, 'advance_id': preinv.id, 'sequence': 1000})
    #                 lines.append(inv_line_id)
    #     inv = self._prepare_invoice(cr, uid, order, lines, context=context)
    #     inv_id = inv_obj.create(cr, uid, inv, context=context)
    #     data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
    #     if data.get('value', False):
    #         inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
    #     inv_obj.button_compute(cr, uid, [inv_id])
    #
    #     return inv_id

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # adaptative function: the system learn

        if not isinstance(ids, (list, tuple)):
            ids = [ids]
         
        if vals.get('carriage_condition_id', False) or vals.get('goods_description_id', False):
            for order in self.browse(cr, uid, ids, context):
                partner_vals = {}
                if not order.partner_id.carriage_condition_id:
                    partner_vals['carriage_condition_id'] = vals.get('carriage_condition_id')
                if not order.partner_id.goods_description_id:
                    partner_vals['goods_description_id'] = vals.get('goods_description_id')
                if partner_vals:
                    self.pool['res.partner'].write(cr, uid, [order.partner_id.id], partner_vals, context)

        return super(sale_order, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # adaptative function: the system learn
        sale_order_id = super(sale_order, self).create(cr, uid, vals, context=context)
        # create function return only 1 id
        if vals.get('carriage_condition_id', False) or vals.get('goods_description_id', False):
            order = self.browse(cr, uid, sale_order_id, context)
            partner_vals = {}
            if not order.partner_id.carriage_condition_id:
                partner_vals['carriage_condition_id'] = vals.get('carriage_condition_id')
            if not order.partner_id.goods_description_id:
                partner_vals['goods_description_id'] = vals.get('goods_description_id')
            if partner_vals:
                self.pool['res.partner'].write(cr, uid, [order.partner_id.id], partner_vals, context)
        return sale_order_id

    def copy(self, cr, uid, ids, default, context=None):
        if not default:
            default = {}
        default.update({
            'minimum_planned_date': False,
        })
        return super(sale_order, self).copy(cr, uid, ids, default, context=context)