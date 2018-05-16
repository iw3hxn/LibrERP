# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

import logging

from osv import fields, orm

import openerp.netsvc as netsvc

_logger = logging.getLogger(__name__)


class mrp_production_wizard(orm.TransientModel):

    _name = 'mrp.production.wizard'
    _inherit = 'ir.wizard.screen'

    _columns = {
        'production_id': fields.many2one('mrp.production', 'Production Order'),
        'production_name': fields.related('production_id', 'name'),
        'move_lines': fields.one2many('stock.move.temp', 'wizard_id', 'Products to Consume', domain=[('is_consumed', '=', False)]),
        'move_lines2': fields.one2many('stock.move.temp', 'wizard_id', 'Consumed Products', domain=[('is_consumed', '=', True)]),
    }

    def confirm_edit_mrp_products(self, cr, uid, ids, context):
        context = self.pool['res.users'].context_get(cr, uid)
        stock_move_obj = self.pool['stock.move']
        for wizard in self.browse(cr, uid, ids, context):
            picking = wizard.production_id.picking_id

            # Reopen associated picking
            picking.action_reopen(context=context)

            # re-elaborate
            picking_lines_ids = [l.id for l in picking.move_lines]
            wizard_lines = wizard.move_lines
            wizard_lines.extend(wizard.move_lines2)
            wizard_lines_ids = [l.orig_stock_move_id.id for l in wizard_lines]

            to_be_removed = [p for p in picking_lines_ids if p not in wizard_lines_ids]
            to_be_added = [p for p in wizard_lines if not p.orig_stock_move_id]

            stock_move_obj.unlink(cr, uid, to_be_removed, context)

            for line in to_be_added:
                vals = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'location_id': line.location_id.id,
                    'location_dest_id': line.location_dest_id.id,
                    'prodlot_id': line.prodlot_id.id,
                    'picking_id': picking.id,
                    'state': line.state
                }
                stock_move_obj.create(cr, uid, vals, context)

            picking.draft_validate(context=context)

            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrp.production', wizard.production_id.id, 'force_production', cr)
            # wf_service.trg_validate(uid, 'mrp.production', wizard.production_id.id, cr)

        return {
            'type': 'ir.actions.act_window_close'
        }
