# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product serial module for OpenERP
#    Copyright (C) 2008 Raphaël Valyi
#    Copyright (C) 2014 Didotech SRL
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


class pallet_move(orm.Model):
    _description = "Pallet Move"
    _name = 'pallet.move'
    _order = 'date'

    _columns = {
        'name': fields.char("Number", size=256 , required=True),
        'date': fields.date('Date', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'move': fields.selection([('in', '+'), ('out', '-')], 'Move', readonly=True),
        'account_invoice_id': fields.many2one('account.invoice', 'Invoice', domain=[('partner_id', '=', 'partner_id')]),
        'stock_picking_id': fields.many2one('stock.picking', 'Picking', domain=[('partner_id', '=', 'partner_id')]),
        'pallet_qty': fields.integer('Number of Pallets'),
        'pallet_id': fields.many2one('product.ul', 'Pallet', domain=[('type', '=', 'pallet')]),
    }
    
    _defaults = {
        'date': fields.date.context_today,
    }
    
    _order ="date desc"
    
    
class product_ul(orm.Model):
    _inherit = 'product.ul'
    
    def get_pallet_sum(self, cr, uid, ids, field_name, args, context):
        pallet_move_obj = self.pool['pallet.move']
        result = {}
        
        if context.get('partner_id', False):
            product_ul_pallet_ids = self.search(cr, uid, [('type', '=', 'pallet')], context=context)
            for product_ul_id in ids:
                if product_ul_id in product_ul_pallet_ids:
                    # pallets_out = pallet_move_obj.search(cr, uid, [('pallet_id', '=', product_ul_id), ('partner_id', '=', context['partner_id']), ('move', '=', 'out')])
                    # pallets_in = pallet_move_obj.search(cr, uid, [('pallet_id', '=', product_ul_id), ('partner_id', '=', context['partner_id']), ('move', '=', 'in')])
                    pallet_move_ids = pallet_move_obj.search(cr, uid, [('pallet_id', '=', product_ul_id), ('partner_id', '=', context['partner_id'])], context=context)
                    if pallet_move_ids:
                        pallet_sum = 0
                        for pallet_move in pallet_move_obj.browse(cr, uid, pallet_move_ids):
                            if pallet_move.move == 'in':
                                pallet_sum -= pallet_move.pallet_qty
                            else:
                                pallet_sum += pallet_move.pallet_qty
                        result[product_ul_id] = pallet_sum
                    else:
                        result[product_ul_id] = 0
                else:
                    result[product_ul_id] = 0
            return result
        else:
            return dict(zip(ids, [0] * len(ids)))
        
    _columns = {
        'pallet_sum': fields.function(get_pallet_sum, string='Pallet Sum', type='integer', method=True),
    }
