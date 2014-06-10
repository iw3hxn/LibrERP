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

from openerp.osv import osv

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'
    
    def create(self, cr, uid, vals, context={}):
        if not vals.get('bom_id', False):
            self.pool.get('product.product').write(cr, uid, vals['product_id'], {'supply_method': 'produce', 'purchase_ok': False})
        return super(mrp_bom, self).create(cr, uid, vals, context=context)
    
    def unlink(self, cr, uid, ids, context={}):
        product_obj = self.pool.get('product.product')
        boms = self.browse(cr, uid, ids)
        
        for product_id in [bom.product_id.id for bom in boms]:
            bom_ids_count = self.search(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], count=True)
            
            if bom_ids_count == 1:
                product_obj.write(cr, uid, product_id, {'supply_method': 'buy', 'purchase_ok': True})
        
        return super(mrp_bom, self).unlink(cr, uid, ids, context=context)
    
    #def _compute_type(self, cr, uid, ids, field_name, arg, context=None):
    #    """ Sets particular method for the selected bom type.
    #    @param field_name: Name of the field
    #    @param arg: User defined argument
    #    @return:  Dictionary of values
    #    """
    #    res = dict.fromkeys(ids, False)
    #    for line in self.browse(cr, uid, ids, context=context):
    #        if line.type == 'phantom' and not line.bom_id:
    #            res[line.id] = 'set'
    #            continue
    #        if line.bom_lines or line.type == 'phantom':
    #            continue
    #        if line.product_id.supply_method == 'produce':
    #            if line.product_id.procure_method == 'make_to_stock':
    #                res[line.id] = 'stock'
    #            else:
    #                res[line.id] = 'order'
    #        if line.product_id and line.product_id.type == 'service':
    #            res[line.id] = 'service'
    #    return res
    #
    #_columns = {
    #    'method': fields.function(_compute_type, string='Method', type='selection', selection=[('',''),('stock','On Stock'),('order','On Order'),('set','Set / Pack'),('service','Service')]),
    #}
