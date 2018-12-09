# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class asset_depreciation_confirmation_wizard(orm.TransientModel):
    _name = "asset.depreciation.confirmation.wizard"
    _description = "asset.depreciation.confirmation.wizard"
    _columns = {
       'period_id': fields.many2one('account.period', 'Period', required=False, help="Choose the period for which you want to automatically post the depreciation lines of running assets"),
       'set_init': fields.boolean('Set init', help='Set depreciation as init for current fiscal year.'),
       'fy_id': fields.many2one('account.fiscalyear', 'Fiscal Year',
        domain="[('state', '=', 'draft')]",
        required=True, help='Calculate depreciation table for asset acquired in this Fiscal Year'),
    }

    def _get_period(self, cr, uid, context=None):
        ctx = dict(context or {}, account_period_prefer_normal=True)
        periods = self.pool.get('account.period').find(cr, uid, context=ctx)
        if periods:
            return periods[0]
        return False

    def _get_default_fiscalyear(self, cr, uid, context=None):
        fiscalyear_id = self.pool['account.fiscalyear'].find(cr, uid, exception=False, context=context)
        if fiscalyear_id:
            return fiscalyear_id
        return False

    _defaults = {
        'period_id': _get_period,
        'fy_id': _get_default_fiscalyear,
    }

    def asset_compute(self, cr, uid, ids, context):
        ass_obj = self.pool.get('account.asset.asset')
        asset_ids = ass_obj.search(cr, uid, [('state', '=', 'open'), ('type', '=', 'normal')], context=context)
        data = self.browse(cr, uid, ids, context=context)
        period_id = data[0].period_id.id
        created_move_ids = ass_obj._compute_entries(cr, uid, asset_ids, period_id, check_triggers=True, context=context)
        return {
            'name': _('Created Asset Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'domain': "[('id','in',["+','.join(map(str,created_move_ids))+"])]",
            'type': 'ir.actions.act_window',
        }

    def asset_set_init(self, cr, uid, ids, context):
        ass_obj = self.pool.get('account.asset.asset')
        data = self.browse(cr, uid, ids, context=context)
        fy = data[0].fy_id
        asset_ids = ass_obj.search(cr, uid, [
            ('state', 'in', ['open', 'draft']),
            ('type', '=', 'normal'),
            # ('date_start', '>=', fy.date_start),
            ('date_start', '<=', fy.date_stop)
            ], context=context)
        asset_board_obj = self.pool['account.asset.depreciation.line']
        set_init = data[0].set_init
        init_move_ids = []
        for asset in ass_obj.browse(cr, uid, asset_ids, context):

            if not asset_board_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '!=', False), ('type', '=', 'depreciate')], context=context):
                if not asset_board_obj.search(cr, uid, [('asset_id', '=', asset.id), ('line_date', '>=', fy.date_start), ('line_date', '<=', fy.date_stop), ('move_id', '=', False), ('init_entry', '=', True)], context=context):
                    asset.compute_depreciation_board()
                asset_board_moves = asset_board_obj.search(cr, uid, [
                        ('asset_id', '=', asset.id),
                        ('line_date', '>=', fy.date_start),
                        ('line_date', '<=', fy.date_stop),
                        ('move_id', '=', False), ('type', '=', 'depreciate')])
                for asset_board in asset_board_obj.browse(
                            cr, uid, asset_board_moves, context):
                    if set_init:
                        asset_board.write({'init_entry': True})
                    init_move_ids.append(asset_board.id)
        return {
            'name': _('Asset Moves Confirmed as Init entry'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.depreciation.line',
            'view_id': False,
            'domain': "[('id','in',[" + ','.join(map(str, init_move_ids)) + "])]",
            'type': 'ir.actions.act_window',
        }
