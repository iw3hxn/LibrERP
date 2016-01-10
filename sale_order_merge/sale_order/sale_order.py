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
import netsvc


class sale_order(orm.Model):
    _inherit = "sale.order"

    def merge_order(self, cr, uid, orders, merge_lines, context=None):
        """ Merge draft order. Work only with same partner.
            You can merge invoices and refund invoices with each other.
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

            if parent.shop_id != order.shop_id:
                raise orm.except_orm(_('Error!'),
                    _('Can not merge order(s) on different shop! {parent} different from {order}').format(parent=parent.shop_id.name, order=order.shop_id.name))

            if order.state != 'draft':
                raise orm.except_orm(_('Error!'), _("You can merge only orders in draft state."))

        parent_id = self.pool['sale.order'].copy(cr, uid, parent.id, context=context)
        parent = self.browse(cr, uid, parent_id, context=context)

        # Merge invoices that are in draft state
        sale_order_line_obj = self.pool['sale.order.line']
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
            for order_line in order.order_line:
                mrg_pdt_ids = sale_order_line_obj.search(cr, uid, [('order_id', '=', parent.id), ('product_id', '=', order_line.product_id.id)], context=context)
                if merge_lines and len(mrg_pdt_ids) == 1:  # product found --> add quantity
                    sale_order_line_obj.write(cr, uid, mrg_pdt_ids, {
                        'product_uom_qty': sale_order_line_obj._can_merge_quantity(cr, uid, mrg_pdt_ids[0], order_line.id)}, context)
                    # sale_order_line_obj.unlink(cr, uid, [order_line.id])
                elif order_line.order_id.id != context['active_id']: # not the same line of initial order
                    order_line_copy_id = sale_order_line_obj.copy(cr, uid, order_line.id, context)
                    vals = {
                        'order_id': parent.id,
                    }
                    sale_order_line_obj.write(cr, uid, order_line_copy_id, vals, context)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'sale.order', order.id, 'cancel', cr)
            # self.unlink(cr, uid, [order.id], context)

        self.write(cr, uid, parent.id, {
            'date_order': datetime.date.today(),
            'origin': origin,
            'note': note,
        }, context)

        self.button_dummy(cr, uid, [parent.id])
        return [parent.id]


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
