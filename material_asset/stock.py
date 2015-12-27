# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Didotech srl (info@didotech.com)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


# ----------------------------------------------------------
# Asset Location
# ----------------------------------------------------------
class asset_location(orm.Model):
    '''
        Add "assets" type to standard location type

        requires "stock" module
    '''
    _name = "stock.location"
    _inherit = "stock.location"

    _columns = {
        'usage': fields.selection([('supplier', 'Supplier Location'), ('view', 'View'), ('customer', 'Customer Location'), ('inventory', 'Inventory'), ('procurement', 'Procurement'), ('production', 'Production'), ('assets', 'Assets'), ('transit', 'Transit Location for Inter-Companies Transfers'), ('internal', 'Internal Location')], 'Location Type', required=True,
                                  help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
                                          \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
                                          \n* Internal Location: Physical locations inside your own warehouses,
                                          \n* Customer Location: Virtual location representing the destination location for products sent to your customers
                                          \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
                                          \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
                                          \n* Assets: Virtual location serving for internal products use
                                          \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
                                         """, select=True),
    }

    _defaults = {
        'usage': 'assets',
    }


class create_asset_onmove(orm.Model):
    """
        Verify if product is moving to "assets" location, if so, create (if missing)
        "asset_product" record, so the product will apear among assets.
    """
    _name = "stock.move"
    _inherit = "stock.move"

    def action_done(self, cr, uid, ids, context=None):
        if context and context.get('asset_created', False):
            return super(create_asset_onmove, self).action_done(cr, uid, ids, context)
        else:
            return self.create_asset(cr, uid, ids, context)

    def create_asset(self, cr, uid, ids, context):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        for move in self.browse(cr, uid, ids, context=context):

            if not move.prodlot_id.id and move.location_dest_id.usage == 'assets':
                prodlot_id = False
            else:
                prodlot_id = move.prodlot_id.id

            # verify that product is not yet an asset:
            asset_product_ids = self.pool['asset.product'].search(cr, uid, [('product_product_id', '=', move.product_id.id), ], context=context)
            if move.location_dest_id.usage == 'assets' and not asset_product_ids:
                # Launch a form and ask about category:
                assign_category_id = self.pool["asset.assign.category"].create(cr, uid, {}, context=dict(context, active_ids=ids))
                return {
                    'name': _("Assign Category"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'asset.assign.category',
                    'res_id': assign_category_id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                    'context': {
                        'serial_number': prodlot_id,
                        'company_id': move.company_id.id,
                        'product_id': move.product_id.id,
                        'location': move.location_dest_id._name + ',' + str(move.location_dest_id.id),
                        'move_ids': ids
                    },
                }

            elif move.location_dest_id.usage == 'assets':
                # control if product is an asset:
                asset_ids = self.pool['asset.asset'].search(cr, uid, [('asset_product_id', '=', asset_product_ids[0]), ('serial_number', '=', prodlot_id), ('serial_number', '!=', False)])
                if not asset_ids:
                    # create asset.asset
                    self.pool['asset.asset'].create(cr, uid, {
                        'asset_product_id': asset_product_ids[0],
                        'serial_number': prodlot_id,
                        'company_id': move.company_id.id,
                        'has_date_option': False,
                        'location': move.location_dest_id._name + ',' + str(move.location_dest_id.id)
                    })

        return super(create_asset_onmove, self).action_done(cr, uid, ids, context)

    def duplicate(self, cr, uid, move_ids, context=None):

        move = self.browse(cr, uid, move_ids[0], context)
        values = {
            'product_qty': 1,
            'product_uom': move.product_uom.id,
            'location_id': move.location_id.id,
            'name': move.name,
            'product_id': move.product_id.id,
            'company_id': move.company_id.id,
            'state': 'draft',
            'location_dest_id': move.location_dest_id.id,
        }
        self.create(cr, uid, values, context)

        res = self.pool['ir.model.data'].get_object_reference(cr, uid, 'material_asset', 'view_product_to_asset')
        return {
            'name': _("From Stock to Asset"),
            'view_mode': 'tree',
            'view_id': res and res[1] or False,
            'view_type': 'form',
            'res_model': 'stock.move',
            'res_id': False,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': "[('location_dest_id.usage', '=', 'assets'), ('state','=','draft')]",
            'context': context
        }
