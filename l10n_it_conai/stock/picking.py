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
import decimal_precision as dp
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class product_category(orm.Model):
    _inherit = "product.category"
    
    _columns = {
        'conai_product_id': fields.many2one(
            'product.product', 'CONAI product to be charged in invoices'),
    }


class stock_move(orm.Model):
    _inherit = "stock.move"
    
    _columns = {
        'weight_exempt_conai': fields.float(
            string='CONAI exempt weight of product',
            digits_compute=dp.get_precision('Stock Weight'),
        ),
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
                        conai_product_id = move_line.product_id.categ_id.conai_product_id
                        if not conai_product_id in res:
                            res.append(conai_product_id)
        
        return res

    def _get_partner_conai_declaration(self, cr, uid, partner_id, picking):
        res = []
        if not partner_id:
            return res
        if not picking:
            return res

        conai_declaration_obj = self.pool['conai.declaration']
        #if len(partner_id) > 1:
            # not possible if more than 1 partner for invoice (controllo inverosimile?)
        #    pass
        picking_date = datetime.strptime(picking.date_done, DEFAULT_SERVER_DATETIME_FORMAT) or \
            datetime.strptime(picking.date, DEFAULT_SERVER_DATETIME_FORMAT)
        res = conai_declaration_obj.search(
            cr, uid, [
                ('partner_id', '=', partner_id.id),
                ('active', '=', True),
                ('date_start_validity', '<=', picking_date),
                ('date_end_validity', '>=', picking_date),
            ]
        )

        return res

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
                              group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id,
                                                               group, type, context)
        invoice_lines = []
        conai_lines = {}
        invoice_obj = self.pool['account.invoice']
        conai_declaration_obj = self.pool['conai.declaration']
        partner_obj = self.pool['res.partner']
        uom_obj = self.pool['product.uom']
        
        for picking in self.browse(cr, uid, ids, context=context):
            invoice = invoice_obj.browse(cr, uid, res[picking.id], context=None)
            #verifica se il partner è esente dal conai
            partner = partner_obj.browse(cr, uid, invoice.partner_id, context=context)
            if partner.is_conai_exempt:
                return res

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
            
            partner_conai_declaration = self._get_partner_conai_declaration(
                cr, uid, invoice.partner_id, picking)
            conai_declaration_ids = []
            if partner_conai_declaration:
                conai_declaration_ids = conai_declaration_obj.browse(
                    cr, uid, partner_conai_declaration, context=None)
            
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                if move_line.scrapped:
                    # do no invoice scrapped products
                    continue
                if move_line.product_id:
                    if move_line.product_id.categ_id.conai_product_id:
                        #se il prodotto del movimento ha un prodotto conai collegato,
                        #aggiungo la quantità alla riga del prodotto conai collegato
                        conai_categ = move_line.product_id.categ_id
                        conai_product = move_line.product_id.categ_id.conai_product_id
                        if conai_product in conai_product_ids:
                            if conai_declaration_ids:
                                #todo trasformare l'unità di peso del prodotto in unità di peso
                                #del prodotto conai
                                import pdb; pdb.set_trace()
                                for conai_declaration in conai_declaration_ids:
                                    if conai_categ == conai_declaration.product_categ_id:
                                        #write amount in conai lines for invoice
                                        percent_exemptation = conai_declaration.percent_exemption or 0.0
                                        amount_exemptation = move_line.weight_net * percent_exemptation
                                        amount_qty = move_line.weight_net - amount_exemptation
                                        # qui va trasformato
                                        ref_uom_weight = uom_obj.search(
                                            cr, uid, [('category_id','=','Weight'),
                                                      ('uom_type','=','reference')])
                                        amount_qty_transformed = uom_obj._compute_qty(
                                            cr, uid, ref_uom_weight[0], amount_qty,
                                                conai_product.uom_id.id)

                                        conai_lines[conai_product.id]['weight_net'] += amount_qty_transformed
                                        #write exempt amount in stock.move
                                        move_line.write({'weight_exempt_conai': amount_exemptation})
                            else:
                                conai_lines[conai_product.id]['weight_net'] += move_line.weight_net
                                #TODO fare il calcolo in base al plafond - se viene usato
            
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
    
            if invoice_lines:
                invoice_obj.button_compute(cr, uid, [invoice.id], context=context)

        return res
