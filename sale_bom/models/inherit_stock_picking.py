# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2013-2014 Didotech srl (info at didotech.com)
#                          All Rights Reserved.
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
###############################################################################

from openerp.osv import orm, fields


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
                            group=False, type='out_invoice', context=None):

        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        invoice_dict = super(stock_picking, self).action_invoice_create(cr, uid,
                            ids, journal_id, group, type, context=context)
        if type != 'out_invoice':
            return invoice_dict
        processed_invoice = []
        for picking_key in invoice_dict:
            if invoice_dict[picking_key] in processed_invoice:
                continue
            processed_invoice.append(invoice_dict[picking_key])
            invoice = self.pool['account.invoice'].browse(cr, uid, invoice_dict[picking_key], context=context)
            if not invoice.company_id.is_group_invoice_line:
                continue

            for line in invoice.invoice_line:
                if line.move_line_id and line.move_line_id.sale_line_id and line.move_line_id.sale_line_id._columns.get('mrp_bom', False) and line.move_line_id.sale_line_id.mrp_bom:

                    qty_delivery = 0
                    for bom_line in line.move_line_id.sale_line_id.mrp_bom:
                        qty_delivery += bom_line.product_uom_qty

                    new_line_vals = {
                        'price_unit': line.move_line_id.sale_line_id.price_unit,
                        'discount': line.move_line_id.sale_line_id.discount,
                        'quantity': line.quantity / qty_delivery,
                    }
                    self.pool['account.invoice.line'].write(cr, uid, line.id, new_line_vals, context=context)
            invoice.button_reset_taxes()
        return invoice_dict
