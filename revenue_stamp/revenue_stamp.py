# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields


class partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'charge_revenue_stamp': fields.boolean('Revenue stamp Charged in Invoice', help="In case VAT free, revenue stamp's cost will be charged in invoices."),
        'charge_invoice_cost': fields.boolean('Costs Charged in Invoice', help="Costs will be charged in invoices."),
        'product_toinvoice_ids': fields.one2many('toinvoice.product', 'product_toinvoice_id', 'Invoice Costs'),
    }


class unique_revenue_product(osv.osv):
    _name = 'unique.revenue.product'
    _description = 'Unique revenue product'
    _columns = {
        'name': fields.char('Description', size=50,),
        'unique_revenue_stamp': fields.boolean('Product for revenue stamp'),
        'min_for_stamp': fields.float('Minimal amount for stamp charged in invoice'),
    }
    _defaults = {
        'min_for_stamp': 77.48,
    }
    _sql_constraints = [
        ('unique_revenue_stamp', 'unique (unique_revenue_stamp)', 'The revenue stamp product must be unique !'),
    ]


class toinvoice_product(osv.osv):
    _name = 'toinvoice.product'
    _columns = {
        'name': fields.char('Notes', size=50,),
        'product_toinvoice_id': fields.many2one('res.partner', 'Partner related'),
        'product_id': fields.many2one('product.product', 'Products to be charged in invoices'),
        'qty': fields.float('Quantity to be invoiced'),
    }


class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'unique_revenue_stamp_id': fields.many2one('unique.revenue.product', 'Product id for revenue stamp'),
    }
    _sql_constraints = [
        ('unique_revenue_stamp_id', 'unique (unique_revenue_stamp_id)', 'The revenue stamp product must be unique !'),
    ]


class account_tax_code(osv.osv):
    _inherit = 'account.tax.code'
    _columns = {
        'stamp_in_invoice': fields.boolean('Stamp Charged in Invoice', help="Revenue stamp's cost charged in invoices."),
    }


class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def button_reset_taxes(self, cr, uid, ids, context=None):
        result = super(account_invoice, self).button_reset_taxes(cr, uid, ids, context)
        self.revenue_stamp(cr, uid, ids, context)
        return result

    def action_number(self, cr, uid, ids, context=None):
        super(account_invoice, self).action_number(cr, uid, ids, context)
        self.revenue_stamp(cr, uid, ids, context)
        return True

    def revenue_stamp(self, cr, uid, ids, context=None):
        """
        This function will add line with revenue stamp charge product:
        If partner has 'charge_revenue_stamp' selected it will add product and cost of revenue stamp
        Else, it will add product without cost
        """

        if not ids:
            return True
        if isinstance(ids, (list, tuple)):
            ids = ids[0]

        product_toinvoice_ids = []

        invoice = self.browse(cr, uid, ids, context)
        if not invoice.partner_id or not invoice.invoice_line:
            return False
        partner = invoice.partner_id
        product_obj = self.pool.get('product.product')
        revenue_product_id = product_obj.search(cr, uid, [('unique_revenue_stamp_id.unique_revenue_stamp', '=', True)])
        if revenue_product_id:
            revenue_product = product_obj.browse(cr, uid, revenue_product_id[0], context)

        if partner.charge_invoice_cost:
            for product_toinvoice_id in partner.product_toinvoice_ids:
                product_toinvoice_ids.append(product_toinvoice_id.product_id.id)

        base_tax_amount = 0.0
        for invoice_tax in invoice.tax_line:
            if invoice_tax.tax_code_id.stamp_in_invoice:
                base_tax_amount += invoice_tax.base_amount

        add_product_stamp = False
        if base_tax_amount >= revenue_product.unique_revenue_stamp_id.min_for_stamp:
            add_product_stamp = True
            if partner.charge_revenue_stamp:
                price = revenue_product.product_tmpl_id.list_price
            else:
                price = 0.0

        for invoice_line in invoice.invoice_line:
            if invoice_line.product_id.id == revenue_product_id[0]:
                add_product_stamp = False
            for invoice_product_id in product_toinvoice_ids:
                if invoice_line.product_id.id == invoice_product_id:
                    product_toinvoice_ids.remove(invoice_product_id)

        invoice_lines = []
        if add_product_stamp:
            invoice_lines.append({
                'name': revenue_product.name,
                'product_id': revenue_product_id[0],
                'quantity': 1.0,
                'uos_id': revenue_product.product_tmpl_id.uom_id.id,
                'price_unit': price,
                'price_subtotal': price,
                'partner_id': partner.id,
                'invoice_id': invoice.id,
                'account_id': invoice.invoice_line[0].account_id.id,
                'company_id': invoice.company_id.id,
            })
        if product_toinvoice_ids:
            partner_toinvoice_products = self.pool.get('toinvoice.product').browse(cr, uid, product_toinvoice_ids, context)
            for partner_toinvoice_product in partner_toinvoice_products:
                invoice_lines.append({
                    'name': partner_toinvoice_product.product_id.name,
                    'product_id': partner_toinvoice_product.product_id.id,
                    'quantity': partner_toinvoice_product.qty,
                    'uos_id': partner_toinvoice_product.product_id.product_tmpl_id.uom_id.id,
                    'price_unit': partner_toinvoice_product.product_id.product_tmpl_id.list_price,
                    'price_subtotal': partner_toinvoice_product.product_id.product_tmpl_id.list_price,
                    'partner_id': partner.id,
                    'invoice_id': invoice.id,
                    'account_id': invoice.invoice_line[0].account_id.id,
                    'company_id': invoice.company_id.id,
                })

        invoice_line_obj = self.pool.get('account.invoice.line')
        for invoice_line in invoice_lines:
            invoice_line_obj.create(cr, uid, invoice_line, context)

        return True
