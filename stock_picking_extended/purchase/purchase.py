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

from openerp.osv import fields, orm


class purchase_order(orm.Model):


##############################################################################
#    
#    ONLY 6.1
#
##############################################################################



    _inherit = "purchase.order"
    '''
    address_id is overridden with partner_id because it's used 2binvoiced
    address_delivery_id is a new field for delivery address
    '''
    _columns = {
        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        res = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        supplier = self.pool['res.partner'].browse(cr, uid, partner_id)
        payment_term = supplier.property_payment_term and supplier.property_payment_term.id or False
        res['value'].update({'payment_term': payment_term})
        return res

    def action_invoice_create(self, cr, uid, ids, context=None):
        inv_id = super(purchase_order, self).action_invoice_create(cr, uid, ids, context=None)
        payment_term = self.browse(cr, uid, ids, context)[0].payment_term
        if payment_term:
            self.pool['account.invoice'].write(cr, uid, inv_id, {'payment_term': payment_term.id})
        return inv_id

    def _prepare_order_picking(self, cr, uid, order, context=None):
        return {
            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
            'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
            'date': order.date_order,
            'type': 'in',
            'address_id': order.partner_address_id.id,
            'address_delivery_id': order.dest_address_id.id or order.partner_address_id.id,
            'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
            'purchase_id': order.id,
            'company_id': order.company_id.id,
            'move_lines' : [],
            'partner_id': order.partner_id.id,
        }
