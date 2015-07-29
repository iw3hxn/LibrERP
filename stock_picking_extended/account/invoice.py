# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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


class account_invoice(orm.Model):
    
    _inherit = 'account.invoice'
        
    _columns = {
        'carriage_condition_id': fields.many2one('stock.picking.carriage_condition', 'Carriage condition'),
        'goods_description_id': fields.many2one('stock.picking.goods_description', 'Description of goods'),
        'transportation_condition_id': fields.many2one(
            'stock.picking.transportation_condition', 'Transportation condition'),
        'address_delivery_id': fields.many2one(
            'res.partner.address', 'Address', states={'draft': [('readonly', False)]}, help='Delivery address of \
            partner'),
        'date_done': fields.datetime('Date Done', help="Date of Completion"),
        'number_of_packages': fields.integer('Number of Packages'),
        'weight': fields.float('Weight'),
        'weight_net': fields.float('Net Weight'),
        'carrier_id': fields.many2one('delivery.carrier', 'Carrier'),
    }

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):

        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,
            date_invoice, payment_term, partner_bank_id, company_id)
        if partner_id:
            partner_address_obj = self.pool['res.partner.address']
            delivery_ids = partner_address_obj.search(
                cr, uid, [('partner_id', '=', partner_id), ('default_delivery_partner_address', '=', True)], context=None)
            if not delivery_ids:
                delivery_ids = partner_address_obj.search(
                    cr, uid, [('partner_id', '=', partner_id), ('type', '=', 'delivery')], context=None)
                if not delivery_ids:
                    delivery_ids = partner_address_obj.search(cr, uid, [('partner_id', '=', partner_id)], context=None)

            partner = self.pool['res.partner'].browse(cr, uid, partner_id)
            result['value']['carriage_condition_id'] = partner.carriage_condition_id.id
            result['value']['goods_description_id'] = partner.goods_description_id.id
            result['value']['address_delivery_id'] = delivery_ids and delivery_ids[0]
        return result

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        # adaptative function: the system learn
        if vals.get('carriage_condition_id', False) or vals.get('goods_description_id', False):
            for invoice in self.browse(cr, uid, [ids], context):
                partner_vals = {}
                if not invoice.partner_id.carriage_condition_id:
                    partner_vals['carriage_condition_id'] = vals.get('carriage_condition_id')
                if not invoice.partner_id.goods_description_id:
                    partner_vals['goods_description_id'] = vals.get('goods_description_id')
                if partner_vals:
                    self.pool['res.partner'].write(cr, uid, [invoice.partner_id.id], partner_vals, context)

        return super(account_invoice, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        # adaptative function: the system learn
        ids = super(account_invoice, self).create(cr, uid, vals, context=context)
        if vals.get('carriage_condition_id', False) or vals.get('goods_description_id', False):
            invoice = self.browse(cr, uid, ids, context)
            partner_vals = {}
            if not invoice.partner_id.carriage_condition_id:
                partner_vals['carriage_condition_id'] = vals.get('carriage_condition_id')
            if not invoice.partner_id.goods_description_id:
                partner_vals['goods_description_id'] = vals.get('goods_description_id')
            if partner_vals:
                self.pool['res.partner'].write(cr, uid, [invoice.partner_id.id], partner_vals, context)

        return ids

class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"
    _columns = {
        'advance_id': fields.many2one('account.invoice', 'Advance invoice'),
        'sequence': fields.integer('Number'),
    }

    _default = {
        'sequence': 10
    }

    _order = 'sequence, id'