# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    Copyright (C) 2013
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

import time
from openerp.osv import orm, fields
from tools import DEFAULT_SERVER_DATE_FORMAT


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"
    _columns = {
        'advance_id': fields.many2one('account.invoice','Advance invoice'),
    }

account_invoice_line()


class sale_order(orm.Model):
    _inherit = "sale.order"
    _columns = {
        'carriage_condition_id': fields.many2one('stock.picking.carriage_condition', 'Carriage condition'),
        'goods_description_id': fields.many2one('stock.picking.goods_description', 'Description of goods'),
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            partner = self.pool['res.partner'].browse(cr, uid, partner_id, context=context)
            result['value']['carriage_condition_id'] = partner.carriage_condition_id.id
            result['value']['goods_description_id'] = partner.goods_description_id.id
        return result

    def _make_invoice(self, cr, uid, order, lines, context=None):
        #implementation to put advance reference in invoices
        inv_obj = self.pool['account.invoice']
        obj_invoice_line = self.pool['account.invoice.line']
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool['sale.order.line'].search(cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)], context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool['sale.order.line'].browse(cr, uid, invoiced_sale_line_ids, context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
                for preline in preinv.invoice_line:
                    inv_line_id = obj_invoice_line.copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit, 'advance_id': preinv.id})
                    lines.append(inv_line_id)
        inv = self._prepare_invoice(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        #start code pre-existant
        #partner = self.pool['res.partner'].browse(cr, uid, order.partner_id.id, context=context)
        self.pool['account.invoice'].write(cr, uid, inv_id, {
            #'order_id': order.id,
            'carriage_condition_id': order.carriage_condition_id.id,
            'goods_description_id': order.goods_description_id.id,
            #'transportation_reason_id': partner.transportation_reason_id.id,
            })
        return inv_id

    def action_ship_create(self, cr, uid, ids, *args):
        super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        for order in self.browse(cr, uid, ids, context={}):
            #partner = self.pool['res.partner'].browse(cr, uid, order.partner_id.id)
            picking_obj = self.pool['stock.picking']
            picking_ids = picking_obj.search(cr, uid, [('sale_id', '=', order.id)])
            for picking_id in picking_ids:
                picking_obj.write(cr, uid, picking_id, {
                    #'order_id': order.id,
                    'carriage_condition_id': order.carriage_condition_id.id,
                    'goods_description_id': order.goods_description_id.id,
                    #'transportation_reason_id': partner.transportation_reason_id.id,
                    })
        return True
