# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from tools.translate import _
import decimal_precision as dp


class split_in_production_lot(orm.TransientModel):
    _inherit = "stock.move.split"

    _columns = {
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_uom': fields.many2one('product.uom', 'UoM'),
        'line_ids': fields.one2many('stock.move.split.lines', 'wizard_id', 'Production Lots'),
        'line_exist_ids': fields.one2many('stock.move.split.lines', 'wizard_exist_id', 'Production Lots'),
        'use_exist': fields.boolean('Existing Lots', help="Check this option to select existing lots in the list below, otherwise you should enter new ones line by line."),
        'location_id': fields.many2one('stock.location', 'Source Location')
    }

    _defaults = {
        'use_exist': False,
    }

    def split_lot_serial(self, cr, uid, ids, context=None):
        """ To split a lot"""
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = self.split_serial(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}

    def split_serial(self, cr, uid, ids, move_ids, context=None):
        """ To split stock moves into production lot

        :param move_ids: the ID or list of IDs of stock move we want to split
        """
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        assert context.get('active_model') == 'stock.move',\
             'Incorrect use of the stock move split wizard'

        inventory_id = context.get('inventory_id', False)
        prodlot_obj = self.pool['stock.production.lot']
        inventory_obj = self.pool['stock.inventory']
        move_obj = self.pool['stock.move']
        new_move = []
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                move_qty = move.product_qty
                quantity_rest = move.product_qty
                new_move = []
                if data.use_exist:
                    lines = [l for l in data.line_exist_ids if l]
                else:
                    lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
                    quantity = line.quantity
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        raise orm.except_orm(_('Processing Error'), _('Production lot quantity %d of %s is larger than available quantity (%d) !') \
                                % (total_move_qty, move.product_id.name, move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        self.pool.get('stock.move').log(cr, uid, move.id, _('Unable to assign all lots to this move!'))
                        return False
                    default_val = {
                        'product_qty': quantity,
                        'product_uos_qty': uos_qty,
                        'state': move.state
                    }
                    if quantity_rest > 0:
                        current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                        if inventory_id and current_move:
                            inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
                        new_move.append(current_move)

                    if quantity_rest == 0:
                        current_move = move.id
                    if line.prodlot_id:
                        prodlot_id = line.prodlot_id and line.prodlot_id.id or False
                    else:
                        prodlot_ids = prodlot_obj.search(cr, uid, [('name', '=', line.name), ('product_id', '=', move.product_id.id)])
                        if not prodlot_ids:
                            prodlot_id = prodlot_obj.create(cr, uid, {
                                'name': line.name,
                                'product_id': move.product_id.id
                            },
                            context=context)
                        else:
                            prodlot_id = prodlot_ids[0]

                    move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'state': move.state})

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        move_obj.write(cr, uid, [move.id], update_val)

        return new_move


class stock_move_split_lines_exist(orm.TransientModel):
    _name = "stock.move.split.lines"
    _description = "Stock move Split lines"
    _columns = {
        'name': fields.char('Production Lot', size=64),
        'quantity': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'wizard_id': fields.many2one('stock.move.split', 'Parent Wizard'),
        'wizard_exist_id': fields.many2one('stock.move.split', 'Parent Wizard (for existing lines)'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot'),
    }
    _defaults = {
        'quantity': 1.0,
    }

    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False,
                        loc_id=False, product_id=False, uom_id=False):
        res = {}
        if prodlot_id:
            res = self.pool['stock.move'].onchange_lot_id(cr, uid, [], prodlot_id, product_qty,
                        loc_id, product_id, uom_id)
            if not res.get('warning'):
                stock_available = self.pool['stock.production.lot'].browse(cr, uid, prodlot_id).stock_available
                res.update({'value': {'quantity': stock_available}})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: