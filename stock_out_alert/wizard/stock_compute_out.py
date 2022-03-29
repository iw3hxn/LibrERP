# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Stock Out Alert
#    Copyright (C) 2013 Enterprise Objects Consulting
#                       http://www.eoconsulting.com.ar
#    Authors: Mariano Ruiz <mrsarm@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import osv, fields

import base64
import logging

from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


class StockComputeOut(osv.osv_memory):
    _name = 'stock.compute.out'
    _description = 'Stock Compute Out'

    _columns = {
        'name': fields.text("Text"),
        'line_ids': fields.one2many('stock.compute.out.line', 'wizard_id', 'Line', readonly=False),
        'sale_order_id': fields.many2one('sale.order', 'Order'),
        'state': fields.selection(
            (('draft', 'draft'), ('done', 'done'))),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }

    def compute_out(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """
        # form_data = self.browse(cr, uid, ids)[0]
        stock_move_model = self.pool['stock.move']
        prod_list = stock_move_model._check_op_stock_availability(cr, uid, context)
        res = stock_move_model._get_stock_out(cr, uid, prod_list, context)

        line_values = []
        for company_id in res:
            for location_id in res[company_id]['locations']:
                location_data = res[company_id]['locations'][location_id]
                for product_data in location_data['products']:
                    vals = {
                        'product_id': product_data['product'].id,
                        'qty': product_data['qty'],
                        'qty_buy': product_data['qty_buy'],
                        'purchase_order': product_data['purchase_order'],
                        'buy': False,
                    }
                    line_values.append(vals)

        mail = stock_move_model._get_email_body(cr, uid, res, context)

        return self.write(cr, uid, ids, {
            'state': 'done',
            'name': mail,
            'line_ids': [(0, 0, vals) for vals in line_values]
        }, context=context)

    def create_order_requirement(self, cr, uid, ids, context=None):
        stock_move_model = self.pool['stock.move']
        # prod_list = stock_move_model._check_op_stock_availability(cr, uid, context)
        # stock_out = stock_move_model._get_stock_out(cr, uid, prod_list, context)
        wizard = self.browse(cr, uid, ids[0], context)
        sale_order_ids = []
        if wizard.sale_order_id:
            sale_order_ids.append(wizard.sale_order_id.id)

        if not sale_order_ids:
            raise osv.except_osv(
                'Error',
                _('Missing Sale Order for main company'))

        order_requirement_ids = []
        order_requirement_line = []
        sequence = 0
        for line in wizard.line_ids:
            if not line.buy:
                continue
            ord_req_line_vals = {
                'sequence': sequence,
                'product_id': line.product_id.id,
                'qty': line.qty_buy,
                'buy': True,
                'user_id': uid
            }
            sequence += 10
            order_requirement_line.append(ord_req_line_vals)

        if len(order_requirement_line) == 0:
            raise osv.except_osv(_("Error"), _("No product out of stock found."))

        order_requirement_values = {
                'sale_order_id': sale_order_ids[0],
                'note': _("Created from Stock Out"),
                'order_requirement_line_ids': [(0, 0, vals) for vals in order_requirement_line]
        }
        order_requirement_ids.append(self.pool['order.requirement'].create(cr, uid, order_requirement_values, context))

        if context.get('force_po'):
            for order_requirement in self.pool['order.requirement'].browse(cr, uid, order_requirement_ids, context):
                for line in order_requirement.order_requirement_line_ids:
                    line.action_open_bom()
                    line.confirm_suppliers()
                order_requirement.write({'state': 'done'})

        mod_model = self.pool['ir.model.data']
        act_model = self.pool['ir.actions.act_window']
        action_id = mod_model.get_object_reference(cr, uid, 'sale_order_requirement', 'action_view_order_requirement')
        action_res = action_id and action_id[1]
        action = act_model.read(cr, uid, action_res, [], context)
        action.update({
            'domain': "[('id', 'in', %s)]" % order_requirement_ids,
        })
        return action
