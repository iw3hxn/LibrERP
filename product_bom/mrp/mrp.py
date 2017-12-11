# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2014 Didotech srl (info@didotech.com)
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

import logging

from openerp.osv import orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class mrp_bom(orm.Model):
    _inherit = 'mrp.bom'
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if not vals.get('bom_id', False):
            self.pool['product.product'].write(
                cr, uid, vals['product_id'],
                {'supply_method': 'produce', 'purchase_ok': False},
                context
            )
        return super(mrp_bom, self).create(cr, uid, vals, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        product_obj = self.pool['product.product']
        bom_ids = []

        for bom in self.browse(cr, uid, ids, context):
            if not bom.bom_id:
                bom_ids.append(bom.id)

        boms = self.browse(cr, uid, bom_ids, context)
        for product_id in [bom.product_id.id for bom in boms]:
            bom_ids_count = self.search(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], count=True)
            
            if bom_ids_count == 1:
                product_obj.write(cr, uid, product_id, {'supply_method': 'buy', 'purchase_ok': True}, context=context)
        
        return super(mrp_bom, self).unlink(cr, uid, ids, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if isinstance(ids, (int, long)):
            ids = [ids]
        boms = self.browse(cr, uid, ids, context)
        for product_old_id in [bom.product_id.id for bom in boms]:
            if vals.get('product_id', False) and not product_old_id == vals['product_id']:
                # on new product set that have bom
                self.pool['product.product'].write(cr, uid, vals['product_id'], {'supply_method': 'produce', 'purchase_ok': False})
                bom_ids_count = self.search(cr, uid, [('product_id', '=', product_old_id), ('bom_id', '=', False)], count=True)
                if bom_ids_count == 1:
                    self.pool['product.product'].write(cr, uid, product_old_id, {'supply_method': 'buy', 'purchase_ok': True})
        return super(mrp_bom, self).write(cr, uid, ids, vals, context=context)

    def action_view_bom(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids, context)[0]

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mrp', 'mrp_bom_tree_view')
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Product BOM'),
            'res_model': 'mrp.bom',
            'view_type': 'tree',
            'view_mode': 'tree',
            'view_id': [view_id],
            'domain': [('product_id', '=', line.product_id.id),
                       ('bom_id', '=', False)],
            # 'target': 'new',
            'res_id': False
        }
