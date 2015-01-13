# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2012-2014 Didotech srl (info@didotech.com)
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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time


def _get_selectable_locations(self, cr, uid, context=None):
    return self.pool['asset.location.property'].get_locations(cr, uid, selectable_only=True, context=context)


class asset_move_create(orm.TransientModel):
    _name = "asset.move.create"
    
    _description = "Create Asset Move"
    _columns = {
        "dest_location": fields.reference("Destination Location", _get_selectable_locations, size=128, required=True),
        "user_id": fields.many2one("res.users", "Moved By", required=True),
        'description': fields.text('Move Description'),
        "move_date": fields.datetime("Move Date", required=True),
        'asset_use_id': fields.many2one('asset.use', 'Utilizzo'),
        # - This line generates a strange error. We need many2many relation
        # 'asset_ids': fields.one2many('asset.asset', 'Assets')
        'asset_ids': fields.many2many('asset.asset', 'asset_move_asset_asset_rel', 'move_id', 'asset_id', 'Assets'),
        'address_id': fields.many2one('res.partner.address', 'Location Address'),
        'show_address': fields.boolean('Invisible field'),
    }
    
    _defaults = {
        'show_address': False,
        'user_id': lambda self, cr, uid, context: uid,
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(asset_move_create, self).default_get(cr, uid, fields, context=context)

        if context is None:
            context = {}
        
        if context['active_model'] == 'asset.asset':
            asset_ids = context and context.get('active_ids', []) or []
        elif context['active_model'] == 'asset.property':
            property_ids = context and context.get('active_ids', []) or []
            properties = self.pool['asset.property'].browse(cr, uid, property_ids, context)
            asset_ids = [asset_property.asset_id.id for asset_property in properties]
        else:
            asset_ids = []

        locations = [model for model, description in _get_selectable_locations(self, cr, uid)]
        if context['active_model'] in locations and not context['active_model'] == 'asset.asset':
            active_ids = context.get('active_ids', [])
            if active_ids:
                dest_location = context['active_model'] + ',' + str(active_ids[0])
            else:
                dest_location = False
        else:
            if len(asset_ids) == 1:
                asset = self.pool.get('asset.asset').browse(cr, uid, asset_ids[0])
                asset_stocks = self.pool['stock.location'].search(cr, uid, [('usage', '=', 'assets')])
                if (asset.location._name == 'stock.location' and asset.location.id not in asset_stocks) or not asset.location._name == 'stock.location':
                    dest_location = 'stock.location,' + str(asset_stocks[0])
                else:
                    dest_location = False
            else:
                dest_location = False
            
        res.update({
            'asset_ids': asset_ids,
            'move_date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'dest_location': dest_location,
        })
        return res
    
    def asset_move_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        asset_obj = self.pool['asset.asset']
        move_obj = self.pool['asset.move']
        move_line_obj = self.pool['asset.move.line']
        
        for data in self.browse(cr, uid, ids, context):
            asset_line_ids = []
            asset_ids = []
            
            asset_use_id = data.asset_use_id
            if data.asset_ids:
                for asset in data.asset_ids:
                    if asset and not asset.location == data.dest_location:
                        asset_ids.append(asset.id)
                        source_stock_location_id = asset.stock_location_id.id
                        
                        if not data.dest_location:
                            raise orm.except_orm(_('Warning!'), _("Unknown destination."))
                        
                        asset_location_property = self.pool['asset.location.property'].get_location(cr, uid, data.dest_location._name)
                        
                        if asset_location_property.type == 'address':
                            dest_location = getattr(data, asset_location_property.location_field)
                            if dest_location:
                                address_id = dest_location.id
                            else:
                                raise orm.except_orm(_('Warning'), _("Please select Location Address"))
                            
                            if asset_location_property.stock_location:
                                dest_stock_location_id = asset_location_property.stock_location.id
                            else:
                                raise orm.except_orm(_('Warning'), _("Please define virtual stock location for '{location}'".format(location=asset_location_property.name)))
                            
                            partner_id = dest_location.partner_id.id
                        elif asset_location_property.type == 'location' and asset_location_property.location_field:
                            dest_location = getattr(data.dest_location, asset_location_property.location_field)
                            dest_stock_location_id = dest_location.id
                            address_id = dest_location.address_id.id
                            partner_id = dest_location.address_id.partner_id.id
                        else:
                            dest_location = data.dest_location
                            address_id = False
                            if asset_location_property.stock_location:
                                dest_stock_location_id = asset_location_property.stock_location.id
                            else:
                                raise orm.except_orm(_('Warning'), _("Please define virtual stock location for '{location}'".format(location=asset_location_property.name)))
                            
                            user = self.pool['res.users'].browse(cr, uid, uid, context)
                            partner_id = user.company_id.partner_id.id
                        
                        if hasattr(dest_location, 'usage') and dest_location.usage in ('customer', 'supplier'):
                            move_type = 'out'
                        elif hasattr(dest_location, 'usage') and dest_location.usage in ('procurement', ):
                            move_type = 'in'
                        else:
                            move_type = 'internal'
                            
                        if not asset['location'] == dest_location:
                            move_line_id = move_line_obj.create(cr, uid, {
                                'name': asset.asset_product_id.product_product_id.name_get()[0][1],
                                'source_location': asset['location'] and '{location._name},{location.id}'.format(location=asset['location']) or False,
                                'dest_location': '{location._name},{location.id}'.format(location=dest_location),
                                'date': data.move_date,
                                'user_id': data.user_id.id,
                                # 'origin': select_rent_asset.order_id.name,
                                'address_id': address_id,
                                'product_id': asset.asset_product_id.product_product_id.id,
                                'product_uom': asset.asset_product_id.uom_id.id,
                                'product_qty': 1,
                                'date_expected': data.move_date,
                                'prodlot_id': asset.serial_number.id,  # Serial number
                                'partner_id': partner_id,
                                'location_id': source_stock_location_id,  # Source location
                                'location_dest_id': dest_stock_location_id,  # Destination location (9 - customer)
                            })
                            
                            if move_line_id:
                                asset_line_ids.append(move_line_id)
                        else:
                            raise orm.except_orm(_('Warning!'), _("Asset [{asset}] should be moved to warehouse first.".format(asset=asset['name'])))
                
                if asset_line_ids:
                    asset_lines = move_line_obj.browse(cr, uid, asset_line_ids, context)
                    stock_move_ids = [asset_move_line.stock_move_id.id for asset_move_line in asset_lines]
                    
                    move_id = move_obj.create(cr, uid, {
                        'name': self.pool['ir.sequence'].get(cr, uid, 'asset.move'),
                        'user_id': data.user_id.id,
                        'dest_location': '{location._name},{location.id}'.format(location=dest_location),
                        'date_done': data.move_date,
                        'move_lines': [(6, 0, stock_move_ids)],
                        'note': data.description or '',
                        'location_id': source_stock_location_id,  # Source location
                        'location_dest_id': dest_stock_location_id,  # Destination location
                        'address_id': address_id,
                        'date': data.move_date,
                        'min_date': data.move_date,
                        'max_date': data.move_date,
                        'partner_id': partner_id,
                        'move_type': 'direct',
                        'auto_picking': False,
                        'type': move_type,
                        'number_of_packages': 0,
                    })
                    
                    if move_id:
                        asset_update = {'location': '{location._name},{location.id}'.format(location=dest_location)}
                        asset_update['asset_use_id'] = asset_use_id and asset_use_id.id or False
                        assets = asset_obj.browse(cr, uid, asset_ids, context)
                        for asset in assets:
                            asset_obj.write(cr, uid, [a.id for a in asset.asset_ids], {'asset_use_id': asset_use_id and asset_use_id.id or False })
                        asset_obj.write(cr, uid, asset_ids, asset_update)
                        
        return {'type': 'ir.actions.act_window_close'}
    
    def onchange_location(self, cr, uid, ids, dest_location, context=None):
        if dest_location:
            model, obj_id = dest_location.split(',')
            
            asset_location_property = self.pool['asset.location.property'].get_location(cr, uid, model)
            
            if asset_location_property.type == 'address':
                domain = [('partner_id', '=', int(obj_id)), ('type', '=', 'delivery')]
                address_ids = self.pool['res.partner.address'].search(cr, uid, domain)
                
                if not address_ids:
                    domain = [('partner_id', '=', int(obj_id))]
                    address_ids = self.pool['res.partner.address'].search(cr, uid, domain)
                
                return {
                    'value': {'show_address': True},
                    'domain': {'address_id': domain}
                }
            else:
                return {
                    'value': {'show_address': False},
                }
        else:
            return {}
