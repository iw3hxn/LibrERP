# -*- coding: utf-8 -*-

#################################################################################
# Autor: Mikel Martin (mikel@zhenit.com)
#    Copyright (C) 2012 ZhenIT Software (<http://ZhenIT.com>). All Rights Reserved
#    $Id$
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

from openerp.osv import fields, orm
from tools.translate import _
import datetime


class sale_order(orm.Model):
    _inherit = "sale.order"

    def merge_order(self, cr, uid, orders, merge_lines, context=None):
        """ Merge draft invoices. Work only with same partner.
            You can merge invoices and refund invoices with echa other.
            Moves all lines on the first invoice.
        """
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        if len(orders) <= 1:
            return False
        parent = self.browse(cr, uid, context['active_id'], context=context)
        for order in orders:
            if parent.partner_id.id != order.partner_id.id:
                raise orm.except_orm(_('Error!'),
                    _('Can not merge order(s) on different partners or states ! {parent} different from {order}').format(parent=parent.partner_id.name, order=order.partner_id.name))

            if order.state != 'draft':
                raise orm.except_orm(_('Error!'), _("You can merge only orders in draft state."))

        # Merge invoices that are in draft state
        sale_order_line_obj = self.pool['sale.order.line']
        name = parent.name or ''
        note = parent.note or ''
        origin = parent.origin or ''

        for order in orders:
            if order.id == parent.id:
                continue

            # check if a line with the same product already exist. if so add quantity. else hang up invoice line to first invoice head.

            if order.note:
                note += ', %s' % order.note
            if order.origin:
                origin += ', %s' % order.origin

            line_ids = sale_order_line_obj.search(cr, uid, [('order_id', '=', order.id)], context=context)

            for order_line in sale_order_line_obj.browse(cr, uid, line_ids, context):
                mrg_pdt_ids = sale_order_line_obj.search(cr, uid, [('order_id', '=', parent.id),
                                                                   ('product_id', '=', order_line.product_id.id)],
                                                         context=context)
                if merge_lines and len(
                        mrg_pdt_ids) == 1 and order.shop_id == parent.shop_id:  # product found --> add quantity
                    sale_order_line_obj.write(cr, uid, mrg_pdt_ids, {
                        'product_uom_qty': sale_order_line_obj._can_merge_quantity(cr, uid, mrg_pdt_ids[0], order_line.id)},
                                              context)
                    sale_order_line_obj.unlink(cr, uid, [order_line.id])
                else:
                    vals = {
                        'order_id': parent.id,
                    }

                sale_order_line_obj.write(cr, uid, order_line.id, vals, context)

            self.write(cr, uid, parent.id, {
                'date_order': datetime.date.today(),
                'origin': origin,
                'name': self.pool['ir.sequence'].get(cr, uid, 'sale.order'),
                'order_line': [(6, 0, sale_order_line_obj.search(cr, uid, [('order_id', '=', parent.id)], context=context))],
                'note': note,
            }, context)

            self.unlink(cr, uid, [order.id], context)

        self.button_dummy(cr, uid, [parent.id])
        return parent.id


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    def _can_merge_quantity(self, cr, uid, id1, id2, context=None):
        qty = False
        order1 = self.browse(cr, uid, id1, context)
        order2 = self.browse(cr, uid, id2, context)

        if order1.product_id.id == order2.product_id.id \
                and order1.price_unit == order2.price_unit \
                and order1.product_uom.id == order2.product_uom.id \
                and order1.discount == order2.discount:
            qty = order1.product_uom_qty + order2.product_uom_qty
        return qty

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
