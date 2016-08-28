# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012-2014 Didotech (<http://www.didotech.com>)
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


class asset_assign_category(orm.TransientModel):
    _name = 'asset.assign.category'
    _description = 'Assign category to a new asset product'
    
    _columns = {
        'category_id': fields.many2one('asset.category', 'Asset Category', required=False),
    }
    
    def assign_category(self, cr, uid, ids, context=None):
        category = self.browse(cr, uid, ids, context=context)[0].category_id

        # add row to assets_product table
        asset_product_id = self.pool['asset.product'].create(cr, uid, {
            'create_uid': uid,
            'has_date_option': False,
            'asset_category_id': category.id,
            'product_product_id': context['product_id'],
        }, context)
        
        ## create asset.asset
        self.pool['asset.asset'].create(cr, uid, {
            'asset_product_id': asset_product_id,
            'serial_number': context['serial_number'],
            'company_id': context['company_id'],
            'location': context['location'],
            'has_date_option': False,
        }, context)

        new_context = context.copy()
        new_context['asset_created'] = True
        self.pool['stock.move'].action_done(cr, uid, context['move_ids'], new_context)
        
        return {'type': 'ir.actions.act_window_close'}
