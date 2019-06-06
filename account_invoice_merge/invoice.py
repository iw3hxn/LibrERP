# -*- coding: utf-8 -*-

#################################################################################
#    Autor: Mikel Martin (mikel@zhenit.com)
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


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def merge_invoice(self, cr, uid, invoices, merge_lines, context=None):
        """ Merge draft invoices. Work only with same partner.
            You can merge invoices and refund invoices with echa other.
            Moves all lines on the first invoice.
        """
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
    
        if len(invoices) <= 1:
            return False
        parent = self.pool['account.invoice'].browse(cr, uid, context['active_id'], context=context)
        for invoice in invoices:
            if parent.partner_id != invoice.partner_id:
                raise orm.except_orm(_("Partners don't match!"), _("Can not merge invoice(s) on different partners or states !. %s different from %s") % parent.partner_id.name, invoice.partner_id.name)
            if parent.payment_term and invoice.payment_term and parent.payment_term != invoice.payment_term or False:
                raise orm.except_orm(_("Payment don't match!"), _("Can not merge invoice(s) on different payment !. {0} different from {1}").format(parent.payment_term and parent.payment_term.name or 'no', invoice.payment_term.name and invoice.payment_term.name or 'no'))
            if invoice.state != 'draft':
                raise orm.except_orm(_("Invalid action !"), _("You can merge only invoices in draft state."))

        # Merge invoices that are in draft state
        invoice_line_obj = self.pool['account.invoice.line']
        sale_order_obj = self.pool['sale.order']
        name = parent.name or ''
        comment = parent.comment or ''
        origin = parent.origin or ''
        
        for invoice in invoices:
            if invoice.id == parent.id:
                continue

            # check if a line with the same product already exist. if so add quantity. else hang up invoice line to first invoice head.
            if invoice.name:
                name += ', %s' % invoice.name
            if invoice.comment:
                comment += ', %s' % invoice.comment
            if invoice.origin:
                origin += ', %s' % invoice.origin
            invoice_line_ids = invoice_line_obj.search(cr, uid, [('invoice_id', '=', invoice.id)], context=context)
            for invoice_line in invoice_line_obj.browse(cr, uid, invoice_line_ids, context):
                mrg_pdt_ids = invoice_line_obj.search(cr, uid, [('invoice_id', '=', parent.id), ('product_id', '=', invoice_line.product_id.id)], context=context)
                if merge_lines and len(mrg_pdt_ids) == 1 and invoice.type == parent.type:  # product found --> add quantity
                    invoice_line_obj.write(cr, uid, mrg_pdt_ids, {'quantity': invoice_line_obj._can_merge_quantity(cr, uid, mrg_pdt_ids[0], invoice_line.id)}, context)
                    invoice_line_obj.unlink(cr, uid, [invoice_line.id], context)
                elif invoice.type == parent.type:
                    vals = {
                        'invoice_id': parent.id,
                    }
                else:
                    vals = {
                        'invoice_id': parent.id,
                        'quantity': -invoice_line.quantity,
                    }

                invoice_line_obj.write(cr, uid, invoice_line.id, vals, context)

            self.write(cr, uid, parent.id, {
                'origin': origin,
                'name': name,
                'comment': comment
            }, context)

            sale_order_ids = sale_order_obj.search(cr, uid, [('invoice_ids', 'in', invoice.id)], context=context)
            sale_order_obj.write(cr, uid, sale_order_ids, {'invoice_ids': [(4, parent.id)]}, context)
            self.write(cr, uid, [invoice.id], {'origin': ''}, context)  # no reopen model
            self.unlink(cr, uid, [invoice.id], context)

        self.button_reset_taxes(cr, uid, [parent.id], context)
        return parent.id


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    def _can_merge_quantity(self, cr, uid, id1, id2, context=None):
        qty = False
        invl1 = self.browse(cr, uid, id1, context)
        invl2 = self.browse(cr, uid, id2, context)

        if invl1.product_id.id == invl2.product_id.id \
            and invl1.price_unit == invl2.price_unit \
                and invl1.uos_id.id == invl2.uos_id.id \
                and invl1.account_id.id == invl2.account_id.id \
                and invl1.discount == invl2.discount:
            qty = invl1.quantity + invl2.quantity
        return qty

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
