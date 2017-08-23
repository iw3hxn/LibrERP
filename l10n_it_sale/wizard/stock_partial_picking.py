# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
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


class stock_partial_picking(orm.TransientModel):
    _inherit = "stock.partial.picking"

    _columns = {
        'tracking_code': fields.char('Pack', size=64),
        'ddt_in_reference': fields.char('In DDT', size=32),
        'ddt_in_date': fields.date('In DDT Date'),
        'type': fields.selection([('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal')],
                                 'Shipping Type', required=True,),

    }

    def save_partial(self, cr, uid, ids, context=None):
        res = super(stock_partial_picking, self).save_partial(cr, uid, ids, context=None)
        partial = self.browse(cr, uid, ids[0], context=context)

        vals = {}
        if partial.ddt_in_reference:
            vals.update({'ddt_in_reference': partial.ddt_in_reference})
        if partial.ddt_in_date:
            vals.update({'ddt_in_date': partial.ddt_in_date})
        if vals:
            partial.picking_id.write(vals)

        return res

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])

        picking_id, = picking_ids
        picking = self.pool['stock.picking'].browse(cr, uid, picking_id, context)
        if 'type' in fields:
            res.update(type=picking.type)
        if 'ddt_in_date':
            if picking.ddt_in_date:
                res.update(ddt_in_date=picking.ddt_in_date)
        if 'ddt_in_reference':
            if picking.ddt_in_reference:
                res.update(ddt_in_reference=picking.ddt_in_reference)

        return res

    def do_partial(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        result = super(stock_partial_picking, self).do_partial(cr, uid, ids, context)
        partial = self.browse(cr, uid, ids, context=context)[0]
        vals = {}
        if partial.ddt_in_reference:
            vals.update({'ddt_in_reference': partial.ddt_in_reference})
        if partial.ddt_in_date:
            vals.update({
                'ddt_in_date': partial.ddt_in_date,
                'date': partial.ddt_in_date}
            )
        if vals:
            if result.get('res_id', False) or context.get('active_id', False):
                self.pool['stock.picking'].write(cr, uid, result.get('res_id', False) or context.get('active_id', False), vals, context)
                move_ids = self.pool['stock.move'].search(cr, uid, [('picking_id', '=', result.get('res_id', False) or context.get('active_id', False))], context=context)
                move_vals = {
                    'date': partial.ddt_in_date,
                }
                self.pool['stock.move'].write(cr, uid, move_ids, move_vals, context)

        if result.get('res_id', False) != context.get('active_id', False):
            context.update({
                'active_id': result.get('res_id', False),
                'active_ids': [result.get('res_id', False)],
                'old_result': result
            })

        if context.get('no_auto_ddt', False) or partial.type in ['in', 'internal']:
            return result
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Assign DDT'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'wizard.assign.ddt',
                # 'res_id': res_id,
                'target': 'new',
                'context': context,
            }

