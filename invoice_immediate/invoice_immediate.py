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
        #'discharge_products_in_invoice': fields.boolean('Discharge products in invoice', help="In case of 'immediate invoice', this flag active system of discharge products from stock."),
        #'partner_shipping_id': fields.many2one('res.partner.address', 'Shipping Address', states={'draft': [('readonly', False)]}, help="Shipping address for current invoice.", domain=[('parent_id', '=', 'parent_id')]),
        'move_products': fields.boolean('Load/unload products in stock', help="In case of 'immediate invoice', this flag activate system of loading/unloading products from/to stock."),
        'picking_id': fields.many2one('stock.picking', 'Stock picking created from invoice immediate'),
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
            
            if invoice.type == 'in_invoice' or invoice.type == 'out_refund':
                picking_type = 'in'
            elif invoice.type == 'out_invoice' or invoice.type == 'in_refund':
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
            
            partner_data = partner_obj.browse(cr, uid, invoice.partner_id.id, context)

            # prende quello 'generico' di stock.location, nell'unico caso (improbabile)
            # non ci sia il dato in res.partner, 'property_stock_customer'.
            if picking_type == 'out':
                if not partner_data.property_stock_customer:
                    customer_location_id = stock_location_obj.search(cr, uid, [('name', '=', 'Customers')])
                    assert customer_location_id, _("Customer location's named 'Customers' not exists. please verify.")
                    customer_location_id = customer_location_id[0]
                else:
                    customer_location_id = int(partner_data.property_stock_customer.id)
                dest_id = customer_location_id
            elif picking_type == 'in':
                dest_id = location_id
                location_id = int(partner_data.property_stock_supplier.id)
            
            invoice_line_ids = invoice_line_obj.search(cr, uid, [('invoice_id', '=', invoice.id)])
            invoice_lines = invoice_line_obj.browse(cr, uid, invoice_line_ids)
            
            for line in invoice_lines:
                if line.product_id and line.product_id.type == 'service' or not line.product_id:
                    continue
                
                if picking_type == 'out':
                    product_qty_new = line.product_id.qty_available - line.quantity
                    note = _('Immediate invoice')
                    if product_qty_new < 0:
                        raise orm.except_orm((_('Warning!'), _('Not enough {product} in stock.').format(product=line.product_id.name)))
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
        
        if isinstance(ids, list):
            object_id = int(ids[0])
        else:
            object_id = int(ids)
            
        invoice_data = self.browse(cr, uid, object_id, context=context)
        origin = vals.get('origin', False) or invoice_data.origin or False

        if vals.get('move_products', False) or invoice_data.move_products or False:
            if not origin and vals.get('state', False) in ('cancel',):
                for invoice in self.browse(cr, uid, ids, context=context):
                    # search if picking is already created and delete
                    if invoice.picking_id:
                        self.pool['stock.picking'].action_reopen(cr, uid, [invoice.picking_id.id], context)
                        self.pool['stock.picking'].action_cancel(cr, uid, [invoice.picking_id.id], context)
                        self.pool['account.invoice'].write(cr, uid, [invoice.id], {'picking_id': False}, context=context)
            elif not origin and vals.get('state', False) in ('open',): # and vals.get('move_id', True):
                self.create_picking(cr, uid, ids, vals['state'], context)
    
        return res
