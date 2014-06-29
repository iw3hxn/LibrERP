# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
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

from openerp.osv import orm, fields


class product_category(orm.Model):
    _inherit = "product.category"
    
    _columns = {
        'conai_product_id': fields.many2one(
            'product.product', 'CONAI product to be charged in invoices'),
    }


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _get_group_product_conai(self, picking):
        if not picking:
            return
        
        res = []
        
        for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                if move_line.scrapped:
                    # do no invoice scrapped products
                    continue
                if move_line.product_id:
                    if move_line.product_id.categ_id.conai_product_id:
                        product_id = move_line.product_id.categ_id.conai_product_id
                        if not product_id in res: 
                            res.append(product_id)
        
        return res

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
                              group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id,
                                                               group, type, context)
        invoice_lines = []
        conai_lines = {}
        for picking in self.browse(cr, uid, ids, context=context):
            invoice = self.pool['account.invoice'].browse(cr, uid, res[picking.id], context=None)
            conai_product_ids = self._get_group_product_conai(picking)
            # create line for every conai product and assign qty to 0
            for conai_product in conai_product_ids:
                if not conai_lines.get(conai_product.id):
                    conai_lines[conai_product.id] = {
                        'name': conai_product.name,
                        'product_id': conai_product.id,
                        'weight_net': 0.0,
                        'uos_id': conai_product.product_tmpl_id.uom_id.id,
                        'price_unit': conai_product.product_tmpl_id.list_price,
                        'price_subtotal': conai_product.product_tmpl_id.list_price,
                        'account_id': conai_product.product_tmpl_id.property_account_income.id,
                    }

            import pdb; pdb.set_trace()
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                if move_line.scrapped:
                    # do no invoice scrapped products
                    continue
                if move_line.product_id:
                    if move_line.product_id.categ_id.conai_product_id:
                        product = move_line.product_id.categ_id.conai_product_id
                        if product in conai_product_ids:
                            conai_lines[product.id]['weight_net'] += move_line.weight_net
            
#TODO mettere le righe nelle righe fattura
# con l'importo corretto secondo le esenzioni del cliente o meno
            
            
            
            for conai_line in conai_lines: 
                invoice_lines.append({
                    'name': conai_lines[conai_line]['name'],
                    'product_id': conai_lines[conai_line]['product_id'],
                    'quantity': conai_lines[conai_line]['weight_net'],
                    'uos_id': conai_lines[conai_line]['uos_id'],
                    'price_unit': conai_lines[conai_line]['price_unit'],
                    'price_subtotal': conai_lines[conai_line]['price_subtotal'],
                    'partner_id': invoice.partner_id.id,
                    'invoice_id': res[picking.id],
                    'account_id': conai_lines[conai_line]['account_id'],
                    'company_id': invoice.company_id.id,
                    'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(
                        cr, uid, move_line, type))],
                })
            

        invoice_line_obj = self.pool.get('account.invoice.line')
        for invoice_line in invoice_lines:
            invoice_line_obj.create(cr, uid, invoice_line, context)

# todo invoke wkfl button reset_taxes to recalculate taxes
        

        return res

    def _prepare_invoice_conai_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        if group:
            name = (picking.name or '') + '-' + move_line.name
        else:
            name = move_line.name
        origin = move_line.picking_id.name or ''
        if move_line.picking_id.origin:
            origin += ':' + move_line.picking_id.origin

        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.product_tmpl_id.\
                    property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_income_categ.id
        else:
            account_id = move_line.product_id.product_tmpl_id.\
                    property_account_expense.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_expense_categ.id
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move_line.product_uos and move_line.product_uos.id or False
        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
            uos_id = move_line.product_uom.id
        return {
            'name': name,
            'origin': origin,
            'invoice_id': invoice_id,
            'uos_id': uos_id,
            'product_id': move_line.product_id.id,
            'account_id': account_id,
            'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
            'discount': self._get_discount_invoice(cr, uid, move_line),
            'quantity': move_line.product_qty or move_line.product_uos_qty, #Carlo: i have to invoice based on delivery
            #'quantity': move_line.product_uos_qty or move_line.product_qty,
            'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
            'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
        }