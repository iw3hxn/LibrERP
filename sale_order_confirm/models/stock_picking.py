# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-2015 Didotech srl (<http://www.didotech.com>)
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
from tools.translate import _


class stock_picking(orm.Model):
    """Modificamos la creación de factura desde albarán para incluir el comportamiento de comisiones"""

    _inherit = 'stock.picking'

    def _invoice_hook(self, cr, uid, picking_browse, invoice_id):
        '''Call after the creation of the invoice'''
        res = super(stock_picking, self)._invoice_hook(cr, uid, picking_browse, invoice_id)
        context = self.pool['res.users'].context_get(cr, uid)
        account_invoice_obj = self.pool['account.invoice']
        account_invoice_line_obj = self.pool['account.invoice.line']
        invoice = account_invoice_obj.browse(cr, uid, invoice_id, context)
        picking = self.browse(cr, uid, picking_browse.id, context)

        if not invoice.fiscal_position:
            if invoice.partner_id.property_account_position:
                invoice.write({'fiscal_position': invoice.partner_id.property_account_position.id})
        if not invoice.payment_term:
            if invoice.partner_id.property_payment_term:
                invoice.write({'payment_term': invoice.partner_id.property_payment_term.id})
        if picking.sale_id:
            for invoice in picking.sale_id.invoice_ids:
                if invoice.advance_order_id:
                    # here i need to check fiscal_position
                    if invoice.fiscal_position.split_invoice_advanced:
                        journal_ids = self.pool['account.journal'].search(cr, uid, [('type', '=', 'sale_refund')], limit=1, context=context)
                        journal_id = journal_ids and journal_ids[0] or False
                        new_invoice_id = account_invoice_obj.copy(cr, uid, invoice.id, {'type': 'out_refund', 'invoice_line': False, 'journal_id': journal_id}, context=context)
                        note = _('Invoice {name}').format(name=invoice.number)
                        for line in invoice.invoice_line:
                            line_vals = {
                                'invoice_id': new_invoice_id,
                                'price_unit': line.price_unit,
                                'sequence': 1000,
                                'note': note
                            }
                            account_invoice_line_obj.copy(cr, uid, line.id, line_vals, context=context)
                    else:
                        for line in invoice.invoice_line:
                            line_vals = {
                                'invoice_id': invoice_id,
                                'price_unit': -line.price_unit,
                                'sequence': 1000,
                            }
                            account_invoice_line_obj.copy(cr, uid, line.id, line_vals, context=context)
                        invoice.button_compute()
                    invoice.write({'advance_order_id': False})
        return res

    def _get_group_keys(self, cr, uid, partner, picking, context=None):
        res = super(stock_picking, self)._get_group_keys(cr, uid, partner, picking, context)
        if picking.sale_id and picking.sale_id.payment_term:
            res = '{0}_{1}'.format(res, picking.sale_id.payment_term.id)
        return res
