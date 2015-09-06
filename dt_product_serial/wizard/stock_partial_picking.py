# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2014 Didotech (<http://www.didotech.com>).
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
from openerp.tools.translate import _
from tools.float_utils import float_compare

LOT_SPLIT_TYPE_SELECTION = [
    ('none', 'None'),
    ('single', 'Single'),
    ('lu', 'Logistical Unit')
]

class stock_partial_picking_line(orm.TransientModel):
    _inherit = "stock.partial.picking.line"
        
    def _get_prodlot_code(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for move in self.browse(cr, uid, ids):
            res[move.id] = move.prodlot_id and move.prodlot_id.name or False
        return res

    def _set_prodlot_code(self, cr, uid, ids, field_name, value, arg, context=None):
        if not value:
            return False
        
        if isinstance(ids, (int, long)):
            ids = [ids]
        
        if not hasattr(self, 'serials'):
            self.serial = {ids[0]: value}
        else:
            if not ids[0] in self.serial and value in self.serial.values():
                raise orm.except_orm(_('Warning'), (_('Serial number {number} is written more than once').format(number=value)))
            else:
                self.serials.append(value)
        
        lot_obj = self.pool['stock.production.lot']
        
        for move in self.browse(cr, uid, ids, context=context):
            product_id = move.product_id.id
            value = value.upper()
            existing_prodlot_ids = lot_obj.search(cr, uid, [('name', '=', value), ('product_id', '=', product_id)])
            if existing_prodlot_ids and not existing_prodlot_ids[0] == move.prodlot_id.id:
                raise orm.except_orm(_('Warning'), (_('Serial number "{number}" is already exists').format(number=value)))
            elif not existing_prodlot_ids:
                prodlot_id = self.pool['stock.production.lot'].create(cr, uid, {
                    'name': value,
                    'product_id': product_id,
                })
                
                move.write({'prodlot_id': int(prodlot_id)})

        return True

    _columns = {
        'new_prodlot_code': fields.function(_get_prodlot_code, fnct_inv=_set_prodlot_code,
                                            method=True, type='char', size=64,
                                            string='Prodlot fast input', select=1
                                            ),
        'split_type': fields.related('product_id', 'lot_split_type', type="selection", selection=LOT_SPLIT_TYPE_SELECTION, string="Split", store=False),
        'tracking_id': fields.many2one('stock.tracking', 'Pack/Tracking'),
        'balance': fields.boolean('Balance'),
        'pallet_qty': fields.integer('Number Pallet'),
        'pallet_id': fields.many2one('product.ul', 'Pallet', domain=[('type', '=', 'pallet')]),
    }

    def onchange_new_prodlot_code(self, cr, uid, ids, new_prodlot_code, product_id, prodlot_id, context=None):
        lot_obj = self.pool['stock.production.lot']
        if new_prodlot_code:
            new_prodlot_code = new_prodlot_code.upper()  # all serial number must be on uppercase
        existing_prodlot_ids = lot_obj.search(cr, uid, [('name', '=', new_prodlot_code), ('product_id', '=', product_id)], context=context)

        move_type = self.pool['stock.partial.picking.line'].browse(cr, uid, ids, context=context)[0].move_id.picking_id.type
        if existing_prodlot_ids:
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            if product.lot_split_type == 'single' and move_type != 'out':
                return {
                    'warning': {
                        'title': _('Warning!'),
                        'message': (_('Serial number "{number}" is already exists').format(number=new_prodlot_code))
                    }
                }
            else:
                existing_lot_id = existing_prodlot_ids[0]
                return {'value': {'prodlot_id': existing_lot_id}}
        else:
            prodlot_id = self.pool['stock.production.lot'].create(cr, uid, {
                'name': new_prodlot_code,
                'product_id': product_id,
            })
            return {'value': {'prodlot_id': prodlot_id}}


class stock_partial_picking(orm.TransientModel):
    _inherit = "stock.partial.picking"
    
    def name_get(self, cr, uid, ids, context=None):
        result = {}

        for picking_id in ids:
            result[picking_id] = '{0} - {1}'.format('Stock parzial picking', picking_id)
        return result
    
    _columns = {
        'tracking_code': fields.char('Pack', size=64),
    }

    def do_partial(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time'
        stock_picking = self.pool['stock.picking']
        stock_move = self.pool['stock.move']
        pallet_move_obj = self.pool['pallet.move']
        uom_obj = self.pool['product.uom']
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date': partial.date
        }
        picking_type = partial.picking_id.type
        pallet = {}
        for wizard_line in partial.move_ids:
            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id

            # Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise orm.except_orm(_('Warning!'), _('Please provide Proper Quantity !'))

            # Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor != 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise orm.except_orm(_('Warning'), _('The uom rounding does not allow you to ship "%s %s", only roundings of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:
                # Check rounding Quantity.ex.
                # picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                # partial delivery: 253g
                # => result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                # Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only roundings of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name = 'stock.picking.' + picking_type
                move_id = stock_move.create(cr, uid, {'name': self.pool['ir.sequence'].get(cr, uid, seq_obj_name),
                                            'product_id': wizard_line.product_id.id,
                                            'product_qty': wizard_line.quantity,
                                            'product_uom': wizard_line.product_uom.id,
                                            'prodlot_id': wizard_line.prodlot_id.id,
                                            'location_id': wizard_line.location_id.id,
                                            'location_dest_id': wizard_line.location_dest_id.id,
                                            'picking_id': partial.picking_id.id
                                                      }, context=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
            
            # Pack tracking
            existing_tracking = wizard_line.tracking_id.id
            
            if existing_tracking:  # avoid creating a tracking twice
                # self.pool['stock.tracking').write(cr, uid, existing_tracking, {'name': partial.tracking_code})
                tracking_id = existing_tracking
            else:
                if partial.tracking_code:
                    tracking_id = self.pool['stock.tracking'].search(cr, uid, [('name', '=', partial.tracking_code)])
                    
                    if not tracking_id:
                        tracking_id = self.pool['stock.tracking'].create(cr, uid, {
                            'name': partial.tracking_code,
                        })
                    else:
                        tracking_id = tracking_id[0]
                    
                    self.pool['stock.move'].write(cr, uid, move_id, {'tracking_id': tracking_id})
                    tracking_id = int(tracking_id)
                else:
                    tracking_id = None
            
            partial_data['move%s' % move_id] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.product_uom.id,
                'prodlot_id': wizard_line.prodlot_id.id,
                'balance': wizard_line.balance,
                'tracking_id': tracking_id,
                'pallet_qty': wizard_line.pallet_qty,
                'pallet_id': wizard_line.pallet_id.id, 
            }
            if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % wizard_line.move_id.id].update(product_price=wizard_line.cost,
                                                                         product_currency=wizard_line.currency.id)
            # compose the pallet list
            if wizard_line.pallet_id.id not in pallet:
                pallet[wizard_line.pallet_id.id] = 0
            pallet[wizard_line.pallet_id.id] += wizard_line.pallet_qty
            
        # here i want to create 2 lines

        for pallet_id, pallet_qty in pallet.iteritems():
            if pallet_qty:
                pallet_move_obj.create(cr, uid, {
                    'name': partial.picking_id.name,
                    'date': partial.picking_id.date,
                    'partner_id': partial.picking_id.partner_id.id,
                    'move': partial.picking_id.type,
                    'stock_picking_id': partial.picking_id.id,
                    'pallet_qty': pallet_qty,
                    'pallet_id': pallet_id,
                })
        
        delivered_pack_id = stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)

        if picking_type == 'in':
            res = self.pool['ir.model.data'].get_object_reference(cr, uid, 'stock', 'view_picking_in_form')
        else:
            res = self.pool['ir.model.data'].get_object_reference(cr, uid, 'stock', 'view_picking_out_form')
        vals = {
            'type': 'ir.actions.act_window',
            'name': 'Delivered',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res[1] or False,
            'res_model': 'stock.picking',
            'nodestroy': True,
            'target': 'current',
            'res_id': int(delivered_pack_id[partial.picking_id.id]),
        }

        if partial.picking_id.id == vals['res_id']:
            vals['type'] = 'ir.actions.act_window_close'
        return vals