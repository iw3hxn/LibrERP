# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Bortolatto Ivan (ivan.bortolatto at didotech.com)
# Copyright (c) 2013 Andrei Levin (andrei.levin at didotech.com)
#
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc


class account_invoice(orm.Model):
    _inherit = 'account.invoice'
    _columns = {
        'move_products': fields.boolean('Load/unload products in stock', help="In case of 'immediate invoice', this flag activate system of loading/unloading products from/to stock."),
        'picking_id': fields.many2one('stock.picking', 'Stock picking'),
        'location_id': fields.many2one(
            'stock.location', 'Location',
            select=True, domain="[('usage', '!=', 'view')]"
        ),
        'carriage_condition_id': fields.many2one('stock.picking.carriage_condition', 'Carriage Condition'),
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
    
    def onchange_move_products(self, cr, uid, ids, part, location_id=None):
        if not part:
            return {'value': {'address_delivery_id': False}}

        addr = self.pool['res.partner'].address_get(cr, uid, [part], ['delivery', 'invoice', 'contact'])

        val = {
            'address_delivery_id': addr['delivery'] or addr['invoice'],
        }
        if not location_id:
            location_id = self.pool['stock.location'].search(cr, uid, [('name', '=', 'Stock')])
        val.update({'location_id': location_id})

        return {'value': val}
    
    def create_picking(self, cr, uid, ids, state=None, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool['stock.picking']
        partner_obj = self.pool['res.partner']
        move_obj = self.pool['stock.move']
        stock_location_obj = self.pool['stock.location']
        currency_obj = self.pool['res.currency']
        uom_obj = self.pool['product.uom']

        if isinstance(ids, (int, long)):
            ids = [ids]

        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.address_delivery_id:
                address_id = invoice.address_delivery_id.id
            else:
                addr = invoice.partner_id and partner_obj.address_get(cr, uid, [invoice.partner_id.id], ['delivery']) or {}
                address_id = addr.get('delivery', False)
            
            if invoice.type == 'in_invoice' or invoice.type == 'out_refund':
                picking_type = 'in'
            elif invoice.type == 'out_invoice' or invoice.type == 'in_refund':
                picking_type = 'out'
            else:
                picking_type = 'out'
            
            picking_id = picking_obj.create(cr, uid, {
                'origin': invoice.number,
                'address_id': address_id,
                'type': picking_type,
                'company_id': invoice.company_id.id,
                'move_type': 'one',
                'note': invoice.comment or "",
                'invoice_state': 'none',
                'auto_picking': True,
                'carriage_condition_id': invoice.carriage_condition_id and invoice.carriage_condition_id.id or False,
                'goods_description_id': invoice.goods_description_id and invoice.goods_description_id.id or False,
                'transportation_condition_id': invoice.transportation_condition_id and invoice.transportation_condition_id.id or False,
                'carrier_id': invoice.carrier_id and invoice.carrier_id.id or False,
                'date': invoice.date_done or invoice.date_invoice,
                'min_date': invoice.date_done or invoice.date_invoice,
                'date_done': invoice.date_done or invoice.date_invoice,
                'number_of_packages': invoice.number_of_packages,
            }, context=context)
            
            self.write(cr, uid, [invoice.id], {'picking_id': picking_id}, context=context)
            
            # location_id = stock_location_obj.search(cr, uid, [('name', '=', 'Stock')])
            # assert location_id, _("Stock location's named 'Stock' not exists. please verify.")
            # location_id = location_id[0]
            #
            if invoice.location_id:
                location_id = invoice.location_id.id
            else:
                location_id = stock_location_obj.search(cr, uid, [('name', '=', 'Stock')])
                assert location_id, _("Stock location's named 'Stock' not exists. please verify.")
                location_id = location_id[0]

            partner = partner_obj.browse(cr, uid, invoice.partner_id.id, context)

            # prende quello 'generico' di stock.location, nell'unico caso (improbabile)
            # non ci sia il dato in res.partner, 'property_stock_customer'.

            if picking_type == 'out':
                if not partner.property_stock_customer:
                    customer_location_id = stock_location_obj.search(cr, uid, [('name', '=', 'Customers')])
                    assert customer_location_id, _("Customer location's named 'Customers' not exists. please verify.")
                    customer_location_id = customer_location_id[0]
                else:
                    customer_location_id = int(partner.property_stock_customer.id)
                dest_id = customer_location_id
            elif picking_type == 'in':
                dest_id = location_id
                location_id = int(partner.property_stock_supplier.id)
            
            # invoice_line_ids = invoice_line_obj.search(cr, uid, [('invoice_id', '=', invoice.id)])
            # invoice_lines = invoice_line_obj.browse(cr, uid, invoice_line_ids)
            product_avail = {}
            for line in invoice.invoice_line:
                if line.product_id and line.product_id.type == 'service' or not line.product_id:
                    continue

                if line.quantity < 0:
                    move_location_id, move_dest_id = dest_id, location_id
                else:
                    move_location_id, move_dest_id = location_id, dest_id

                uos_coeff = line.product_id.uos_coeff
                vals = {
                    'name': line.name,
                    'product_qty': abs(line.quantity),
                    'product_uom': line.uos_id.id,
                    'product_uos_qty': abs(line.quantity) * uos_coeff,
                    'product_uos': line.product_id.uos_id.id,
                    'picking_id': picking_id,
                    'product_id': line.product_id.id,
                    'tracking_id': False,
                    'state': 'draft',
                    'location_id': move_location_id,
                    'location_dest_id': move_dest_id,
                    'note': (picking_type == 'out') and _('Immediate invoice') or '',
                    'price_unit': line.price_unit,
                    'price_currency_id': invoice.currency_id.id,
                    'date': invoice.date_done or invoice.date_invoice,
                    'date_expected': invoice.date_done or invoice.date_invoice,
                }
                
                move_obj.create(cr, uid, vals, context=context)

                # Average price computation
                if (picking_type == 'in') and (line.product_id.cost_method == 'average'):
                    product = line.product_id
                    move_currency_id = invoice.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, line.uos_id.id, line.quantity, line.product_id.uom_id.id)
                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, invoice.currency_id.id,
                                move_currency_id, line.price_unit)
                        new_price = uom_obj._compute_price(cr, uid, line.uos_id.id, new_price,
                                product.uom_id.id)
                        if product.qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id]) + (new_price * qty)) / (product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product.write({'standard_price': new_std_price})

            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            picking_obj.force_assign(cr, uid, [picking_id], context)

            for move_line in picking_obj.browse(cr, uid, [picking_id], context)[0].move_lines:
                move_line.write(
                    {
                        'date': invoice.date_done or invoice.date_invoice,
                        'date_expected': invoice.date_done or invoice.date_invoice,
                    })
            picking_obj.write(cr, uid, [picking_id], {
                'min_date': invoice.date_done or invoice.date_invoice,
                'date_done': invoice.date_done or invoice.date_invoice,
            }, context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'picking_id': False,
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        
        if not ids:
            return True
        
        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)

        if isinstance(ids, (int, long)):
            ids = [ids]

        for invoice in self.browse(cr, uid, ids, context=context):
            if vals.get('move_products', False) or invoice.move_products or False:
                origin = vals.get('origin', False) or invoice.origin or False
                if not origin and vals.get('state', False) in ('cancel',):
                    # search if picking is already created and delete
                    if invoice.picking_id:
                        invoice.picking_id.action_reopen()
                        invoice.picking_id.unlink()
                        invoice.write({'picking_id': False})
                elif not origin and vals.get('state', False) in ('open',):  # and vals.get('move_id', True):
                    self.create_picking(cr, uid, ids, vals['state'], context)
    
        return res
