# -*- coding: utf-8 -*-


import datetime


from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.osv import orm, fields
from openerp.tools.translate import _
from tools.float_utils import float_compare


class StockProductionLotReconcile(orm.TransientModel):

    _name = 'stock.production.lot.reconcile'
    _description = 'Stock Move line reconcile'
    _columns = {
        'trans_nbr': fields.integer('# of Transaction', readonly=True),
        'credit': fields.float('Credit', readonly=True),
        'debit': fields.float('Debit', readonly=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(StockProductionLotReconcile, self).default_get(cr, uid, fields, context=context)
        data = self.trans_rec_get(cr, uid, context['active_ids'], context)
        if 'trans_nbr' in fields:
            res.update({'trans_nbr': data['trans_nbr']})
        if 'credit' in fields:
            res.update({'credit': data['credit']})
        return res

    def trans_rec_get(self, cr, uid, ids, context=None):
        stock_production_lot_model = self.pool['stock.production.lot']
        context = context or self.pool['res.users'].context_get(cr, uid)
        stock_production_lots = stock_production_lot_model.browse(cr, uid, context['active_ids'], context=context)
        if len(list(set(stock_production_lots.mapped('product_id')))) != 1:
            raise orm.except_orm(_('Processing Error'), _('For Reconcile you must select same product'))
        stock_available = sum(stock_production_lots.mapped('stock_available'))

        return {'trans_nbr': len(context['active_ids']), 'credit': stock_available}

    def trans_rec_reconcile_full(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        stock_production_lot_model = self.pool['stock.production.lot']
        stock_move_model = self.pool['stock.move']
        stock_picking_model = self.pool['stock.picking']
        date = datetime.datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if 'location_id' not in context:
            # stock.stock_location_stock
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock',
                                                                                              'stock_location_stock')
            locations = [location_id]
        else:
            locations = context['location_id'] and [context['location_id']] or []
        location = locations[0]

        if 'active_ids' in context and context['active_ids']:
            stock_picking_vals = {
                'name': '/',
                'origin': _('LOT INV'),
                'move_type': 'one',
                'type': 'internal'
            }
            picking_id = stock_picking_model.create(cr, uid, stock_picking_vals, context)

            move_ids = []
            stock_moves = stock_production_lot_model.browse(cr, uid, context['active_ids'], context=context)
            qty = min(stock_moves.mapped('stock_available'))

            for line in stock_moves:
                change = qty if line.stock_available > 0 else -qty
                lot_id = line.id
                if change:
                    location_id = line.product_id.product_tmpl_id.property_stock_inventory.id
                    value = {
                        'name': _('LOT INV'),
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'prodlot_id': lot_id,
                        'date': date,
                        'origin': _('LOT INV'),
                        'picking_id': picking_id
                    }

                    if change > 0:
                        value.update({
                            'product_qty': change,
                            'location_id': location_id,
                            'location_dest_id': location,
                        })
                    else:
                        value.update({
                            'product_qty': -change,
                            'location_id': location,
                            'location_dest_id': location_id,
                        })
                    move_ids.append(stock_move_model.create(cr, uid, value, context))

            stock_move_model.action_confirm(cr, uid, move_ids, context=context)
            stock_move_model.action_done(cr, uid, move_ids, context=context)
            stock_move_model.write(cr, uid, move_ids, {'name': _('LOT INV')})
            stock_picking_model.write(cr, uid, picking_id, {'state': 'done'})
        return {'type': 'ir.actions.act_window_close'}
