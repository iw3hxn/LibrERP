# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import orm, fields
from tools.translate import _
import netsvc
import pooler


class sale_order_cancel(orm.TransientModel):
    """
    This wizard will cancel the all the selected invoices.
    If in the journal, the option allow cancelling entry is not selected then it will give warning message.
    """

    _name = "sale.order.cancel"
    _description = "Cancel the Selected Sale Order"

    def order_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        sale_orders = self.pool['sale.order'].browse(cr, uid, context['active_ids'], context=context)

        for order in sale_orders:
            for sale_order_line in order.order_line:
                for move in sale_order_line.move_ids:
                    move.write({'state': 'draft'})
                    move.unlink()

            for picking in order.picking_ids:
                picking.write({'state': 'draft'})
                picking.unlink()

            for invoice in order.invoice_ids:
                if invoice.state == 'draft':
                    invoice.unlink()
            order.write({'state': 'draft'})
            order.unlink()

        return {'type': 'ir.actions.act_window_close'}
