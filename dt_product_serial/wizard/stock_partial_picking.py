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

    def _get_color_line(self, cr, uid, picking_line, product_ids=[], context=None):
        if picking_line.product_id.id in product_ids:
            color = 'blue'
        elif picking_line.tracking:
            color = 'red'
        elif picking_line.line_check or context.get('line_check', False):
            color = 'grey'
        else:
            color = 'black'
        return color

    def action_check(self, cr, uid, move_ids, context):
        line = self.pool['stock.partial.picking.line'].browse(cr, uid, move_ids, context)[0]
        color = self._get_color_line(cr, uid, line, [], context)
        line_vals = {
            'line_check': not line.line_check,
            'row_color': color
        }
        line.write(line_vals)
        return True

    def action_add(self, cr, uid, move_ids, context):
        line = self.pool['stock.partial.picking.line'].browse(cr, uid, move_ids, context)[0]
        dest_qty = line.quantity + 1
        if line.move_id.product_qty >= dest_qty:
            line.write({'quantity': dest_qty})
        return True

    def action_remove(self, cr, uid, move_ids, context):
        line = self.pool['stock.partial.picking.line'].browse(cr, uid, move_ids, context)[0]
        if line.quantity >= 1.0:
            line.write({'quantity': line.quantity - 1})
        return True
        
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

    def get_color(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = 'black'
            if line.tracking:
                res[line.id] = 'red'
        return res

    def _product_code(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        product_obj = self.pool['product.product']

        for line in self.browse(cr, uid, ids, context=context):
            partner_id = line.move_id.partner_id and line.move_id.partner_id.id or None
            code = product_obj._get_partner_code_name(cr, uid, [], line.product_id, partner_id, context=context)['code']
            if code != line.product_id.default_code:
                res[line.id] = code
            else:
                res[line.id] = line.move_id.purchase_line_id and line.move_id.purchase_line_id.name or ''
        return res

    _columns = {
        'code': fields.function(_product_code, type='char', string='Supplier Reference'),
        'row_color': fields.char(string='Row color'),
        'new_prodlot_code': fields.function(_get_prodlot_code, fnct_inv=_set_prodlot_code,
                                            method=True, type='char', size=64,
                                            string='Prodlot fast input', select=1
                                            ),
        'split_type': fields.related('product_id', 'lot_split_type', type="selection", selection=LOT_SPLIT_TYPE_SELECTION, string="Split", store=False),
        'tracking_id': fields.many2one('stock.tracking', 'Pack/Tracking'),
        'balance': fields.boolean('Balance'),
        'pallet_qty': fields.integer('Number Pallet'),
        'pallet_id': fields.many2one('product.ul', 'Pallet', domain=[('type', '=', 'pallet')]),
        'line_check': fields.boolean('Check'),
    }

    def onchange_new_prodlot_code(self, cr, uid, ids, new_prodlot_code, product_id, prodlot_id, context=None):
        lot_obj = self.pool['stock.production.lot']
        if new_prodlot_code:
            new_prodlot_code = new_prodlot_code.upper()  # all serial number must be on uppercase
        existing_prodlot_ids = lot_obj.search(cr, uid, [('name', '=', new_prodlot_code), ('product_id', '=', product_id)], limit=1, context=context)
        existing_lot = lot_obj.browse(cr, uid, existing_prodlot_ids, context)
        move_type = self.pool['stock.partial.picking.line'].browse(cr, uid, ids, context=context)[0].move_id.picking_id.type
        if existing_lot:
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            if product.lot_split_type == 'single' and move_type != 'out' and existing_lot[0].stock_available > 0:
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
            result[picking_id] = '{0} - {1}'.format('Stock partial picking', picking_id)
        return result
    
    _columns = {
        'tracking_code': fields.char('Pack', size=64),
        'product_search': fields.char('Search Product', size=64),
        'arrival_date': fields.date('Real arrival date')
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)

        for line in res.get('move_ids', []):
            if line.get('product_id', False) and line.get('move_id', False):
                move = self.pool['stock.move'].browse(cr, uid, line['move_id'], context=context)
                product = self.pool['product.product'].browse(cr, uid, line['product_id'], context=context)

                if (move.picking_id.type == 'in' and product.track_incoming) or (move.picking_id.type == 'out' and product.track_outgoing):
                    line['tracking'] = True
                    line['row_color'] = 'red'
        return res

    def onchange_product_search(self, cr, uid, ids, product_search, move_ids, context):
        product_obj = self.pool['product.product']
        if product_search:
            product_ids = product_obj.search(cr, uid, ['|', '|', '|',
                                                       ('ean13', '=', product_search),
                                                       ('supplier_code', '=', product_search),
                                                       ('default_code', '=', product_search),
                                                       ('name', 'ilike', product_search)
                                                       ], context=context)
        else:
            product_ids = []
        for line in move_ids:
            if line[0] in [1, 4] and line[1]:
                picking_line = self.pool['stock.partial.picking.line'].browse(cr, uid, line[1], context)
                context_copy = context.copy()
                if line[2] and line[2].get('line_check', False):
                    context_copy.update({'line_check': line[2].get('line_check', False)})
                color = self.pool['stock.partial.picking.line']._get_color_line(cr, uid, picking_line, product_ids, context_copy)
                line[0] = 1  # update
                row_color = {'row_color': color}
                if line[2]:
                    line[2].update(row_color)
                else:
                    line[2] = row_color

        return {'value': {'move_ids': move_ids}}

    def action_set_zero_all(self, cr, uid, move_ids, context):
        for line in self.pool['stock.partial.picking'].browse(cr, uid, move_ids, context)[0].move_ids:
            line.write({'quantity': 0})
        return True

    def action_set_zero_except_check(self, cr, uid, move_ids, context):
        for line in self.pool['stock.partial.picking'].browse(cr, uid, move_ids, context)[0].move_ids:
            if not line.line_check:
                line.write({'quantity': 0})
        return True

    def action_set_max(self, cr, uid, move_ids, context):
        for line in self.pool['stock.partial.picking'].browse(cr, uid, move_ids, context)[0].move_ids:
            line.write({'quantity': line.move_id.product_qty})
        return True

    def action_set_max_except_check(self, cr, uid, move_ids, context):
        for line in self.pool['stock.partial.picking'].browse(cr, uid, move_ids, context)[0].move_ids:
            if not line.line_check:
                line.write({'quantity': line.move_id.product_qty})
        return True

    def save_partial(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time'
        partial = self.browse(cr, uid, ids[0], context=context)
        for line in partial.move_ids:
            if line.line_check:
                vals = {
                    'check_product_qty': line.quantity,
                    'line_check': line.line_check
                }
                if line.prodlot_id:
                    vals.update({'prodlot_id': line.prodlot_id.id})
                if line.move_id.product_uom != line.product_uom:
                    vals.update({'check_product_uom': line.product_uom.id})
                line.move_id.write(vals)

        return {'type': 'ir.actions.act_window_close'}

    def _partial_move_for(self, cr, uid, move):
        partial_move = {
            'product_id': move.product_id.id,
            'product_uom': move.check_product_uom and move.check_product_uom.id or move.product_uom.id,
            'prodlot_id': move.prodlot_id.id,
            'move_id': move.id,
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
            'line_check': move.line_check,
        }
        if move.line_check:
            partial_move.update({'quantity': move.check_product_qty})
        else:
            partial_move.update({'quantity': move.state in ('assigned', 'draft') and move.product_qty or 0})

        if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
            partial_move.update(update_cost=True, **self._product_cost_for_average_update(cr, uid, move))
        return partial_move

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

            # Quantity must be Positive
            if wizard_line.quantity < 0:
                raise orm.except_orm(_('Warning!'), _('Please provide Proper Quantity !'))

            if wizard_line.quantity > 0 and wizard_line.tracking and not (wizard_line.prodlot_id or wizard_line.new_prodlot_code):
                raise orm.except_orm(_('Error!'), _('Please provide lot on product "%s"' % wizard_line.product_id.name))

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
                    raise orm.except_orm(_('Warning'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only roundings of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name = 'stock.picking.' + picking_type
                move_id = stock_move.create(cr, uid, {
                    'name': self.pool['ir.sequence'].get(cr, uid, seq_obj_name),
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
                }, context=context)
        
        delivered_pack_id = stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)

        if picking_type == 'in':
            res = self.pool['ir.model.data'].get_object_reference(cr, uid, 'stock', 'view_picking_in_form')
        else:
            res = self.pool['ir.model.data'].get_object_reference(cr, uid, 'stock', 'view_picking_out_form')

        vals = {
            'type': 'ir.actions.act_window',
            'name': _('Delivered'),
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
