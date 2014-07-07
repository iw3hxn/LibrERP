# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields
import netsvc
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class repair_order_norepair(orm.TransientModel):
    _name = 'repair.order.norepair'
    _description = 'Not repairable Repair Order'
    _columns = {
        'repair_id': fields.many2one('repair.order', "Repair Order", required=True),
        'moveable': fields.boolean("able to move"),
        'partner_id': fields.many2one('res.partner', "Partner"),
        'address_id': fields.many2one('res.partner.address', "Deliver to ")
    }

    def create_delivery(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        wf_service = netsvc.LocalService("workflow")
        #pdb.set_trace()
        for record in self.browse(cr, uid, ids, context=context):
            picking_id = False
            order = record.repair_id or self.pool['repair.order'].browse(cr, uid, context.get('active_id', False), context=context)
            if not order:
                continue
            loc_id = record.partner_id.property_stock_supplier.id
            istate = 'none'
            address_id = record.address_id.id

            pick_name = self.pool['ir.sequence'].get(cr, uid, 'stock.picking.out')
            picking_id = self.pool['stock.picking'].create(cr, uid, {
                'name': pick_name,
                'origin': order.name,
                'type': 'out',
                'address_id': address_id,
                'invoice_state': istate,
                'company_id': order.company_id.id,
                'move_lines': [],
            })
            self.pool['repair.order'].write(cr, uid, [order.id], {'out_picking2producer_id': picking_id, 'repairable': False})
            wf_service.trg_validate(uid, 'repair.order', order.id, 'action_analyzing_end', cr)
            wf_service.trg_validate(uid, 'repair.order', order.id, 'repair_confirm', cr)
            if order.product_id:
                source = order.location_id and order.location_id.id or (order.warehouse_id and order.warehouse_id.lot_input_id.id or False)
                new_prodlot = None
                if order.in_picking_id:
                    move_lines = self.pool['stock.move'].search(cr, uid, [('picking_id', '=', order.in_picking_id.id), ('product_id', '=', order.product_id.id)])
                    if len(move_lines) > 0:
                        product_move = self.pool['stock.move'].browse(cr, uid, move_lines[0])
                        if product_move.prodlot_id:
                            new_prodlot = product_move.prodlot_id.id
                move_vals = {
                    'name': order.name + ': ' + order.manufacturer_pname or '' + order.manufacturer_pref and "[%s]" % (order.manufacturer_pref) or '',
                    'product_id': order.product_id.id,
                    'product_qty': 1,
                    'product_uos_qty': 1,
                    'product_uom': order.product_id.uom_id.id,
                    'product_uos': order.product_id.uom_id.id,
                    'date': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'date_expected': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'location_id': source,
                    'location_dest_id': loc_id,
                    'picking_id': picking_id,
                    'state': 'draft',
                    'company_id': order.company_id.id,
                    'prodlot_id': new_prodlot,
                }
                stock_move_obj = self.pool['stock.move']
                move = stock_move_obj.create(cr, uid, move_vals)
                stock_move_obj.action_confirm(cr, uid, [move])
                stock_move_obj.force_assign(cr, uid, [move])
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return {'type': 'ir.actions.act_window_close'}

    def on_change_partner(self, cr, uid, ids, customer_id):
        if customer_id:
            return {'value': {'moveable': True}}
        return {'value': {'moveable': False}}
