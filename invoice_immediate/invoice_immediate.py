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

from osv import fields, osv
from openerp.tools.translate import _
import netsvc


class account_invoice(osv.Model):
    _inherit = 'account.invoice'
    _columns = {
        #'discharge_products_in_invoice': fields.boolean('Discharge products in invoice', help="In case of 'immediate invoice', this flag active system of discharge products from stock."),
        #'partner_shipping_id': fields.many2one('res.partner.address', 'Shipping Address', states={'draft': [('readonly', False)]}, help="Shipping address for current invoice.", domain=[('parent_id', '=', 'parent_id')]),
        'move_products': fields.boolean('Load/unload products in stock', help="In case of 'immediate invoice', this flag activate system of loading/unloading products from/to stock."),
    }
    
    def onchange_move_products(self, cr, uid, ids, part):
        if not part:
            return {'value': {'address_delivery_id': False}}

        addr = self.pool['res.partner'].address_get(cr, uid, [part], ['delivery', 'invoice', 'contact'])
        part = self.pool['res.partner'].browse(cr, uid, part)
        val = {
            'address_delivery_id': addr['delivery'] or addr['invoice'],
        }

        return {'value': val}
    
    def create_picking(self, cr, uid, ids, state, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool['stock.picking']
        partner_obj = self.pool['res.partner']
        move_obj = self.pool['stock.move']
        stock_location_obj = self.pool['stock.location']
        invoice_line_obj = self.pool['account.invoice.line']

        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.address_delivery_id:
                address_id = invoice.address_delivery_id.id
            else:
                addr = invoice.partner_id and partner_obj.address_get(cr, uid, [invoice.partner_id.id], ['delivery']) or {}
                address_id = addr.get('delivery', False)
            
            if invoice.type == 'in_invoice':
                picking_type = 'in'
            elif invoice.type == 'out_invoice':
                picking_type = 'out'
            else:
                picking_type = 'out'
            
            picking_id = picking_obj.create(cr, uid, {
                'origin': invoice.name,
                'address_id': address_id,
                'type': picking_type,
                'company_id': invoice.company_id.id,
                'move_type': 'direct',
                'note': invoice.comment or "",
                'invoice_state': 'none',
                'auto_picking': True,
                'carriage_condition_id': invoice.carriage_condition_id and invoice.carriage_condition_id.id or False,
                'goods_description_id': invoice.goods_description_id and invoice.goods_description_id.id or False,
                'transportation_condition_id': invoice.transportation_condition_id and invoice.transportation_condition_id.id or False,
                'carrier_id': invoice.carrier_id and invoice.carrier_id.id or False,
                'date_done': invoice.date_done,
                'number_of_packages': invoice.number_of_packages,
            }, context=context)
            
            self.write(cr, uid, [invoice.id], {'picking_id': picking_id}, context=context)
            
            location_id = stock_location_obj.search(cr, uid, [('name', '=', 'Stock')])
            assert location_id, _("Stock location's named 'Stock' not exists. please verify.")
            location_id = location_id[0]
            
            partner_data = partner_obj.read(cr, uid, invoice.partner_id.id, ['property_stock_customer', 'property_stock_supplier'], context)

            # prende quello 'generico' di stock.location, nell'unico caso (improbabile)
            # non ci sia il dato in res.partner, 'property_stock_customer'.
            if picking_type == 'out':
                if not partner_data['property_stock_customer']:
                    customer_location_id = stock_location_obj.search(cr, uid, [('name', '=', 'Customers')])
                    assert customer_location_id, _("Customer location's named 'Customers' not exists. please verify.")
                    customer_location_id = customer_location_id[0]
                else:
                    customer_location_id = int(partner_data['property_stock_customer'][0])
                dest_id = customer_location_id
            elif picking_type == 'in':
                dest_id = location_id
                location_id = int(partner_data['property_stock_supplier'][0])
            
            invoice_line_ids = invoice_line_obj.search(cr, uid, [('invoice_id', '=', invoice.id)])
            invoice_lines = invoice_line_obj.browse(cr, uid, invoice_line_ids)
            
            for line in invoice_lines:
                if line.product_id and line.product_id.type == 'service' or not line.product_id:
                    continue
                
                if picking_type == 'out':
                    if state == 'cancel':
                        product_qty_new = line.product_id.qty_available + line.quantity
                        location_id, dest_id = dest_id, location_id
                        note = _('Invoice cancellation')
                    else:
                        product_qty_new = line.product_id.qty_available - line.quantity
                        note = _('Immediate invoice')
                        
                    if product_qty_new < 0:
                        raise osv.except_osv(_('Warning!'), _('Insufficent quantity of {product}s in stock.'.format(product=line.product_id.name)))
                else:
                    note = ''
                
                if line.quantity < 0:
                    location_id, dest_id = dest_id, location_id

                vals = {
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id,
                    'product_id': line.product_id.id,
                    'product_uos_qty': abs(line.quantity),
                    'product_qty': abs(line.quantity),
                    'tracking_id': False,
                    'state': 'draft',
                    'location_id': location_id,
                    'location_dest_id': dest_id,
                    'note': note
                }
                
                move_obj.create(cr, uid, vals, context=context)
                if line.quantity < 0:
                    location_id, dest_id = dest_id, location_id

            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            picking_obj.force_assign(cr, uid, [picking_id], context)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        
        if not ids:
            return True
        
        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        
        if isinstance(ids, list):
            object_id = int(ids[0])
        else:
            object_id = int(ids)
            
        invoice_data = self.read(cr, uid, object_id)
            
        if 'origin' in vals:
            origin = vals['origin']
        else:
            origin = invoice_data['origin']
             
        state = ''
        if 'state' in vals:
            state = vals['state']
            
        move_products = False
        if 'move_products' in vals:
            move_products = vals['move_products']
        else:
            move_products = invoice_data['move_products']

        if move_products:
            if not origin and state in ('open', 'cancel') and vals.get('move_id', True):
                self.create_picking(cr, uid, ids, state, context)
    
        return res
