# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import decimal_precision as dp
from openerp.osv import orm, fields
from tools.translate import _


class product_product(orm.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    
    _columns = {
        'list_price_copy': fields.related('list_price', type="float", readonly=True, store=False, string='Sale Price', digits_compute=dp.get_precision('Sale Price'),
                                  help='Base price for computing the customer price. Sometimes called the catalog price.'),
        'can_modify_prices': fields.boolean('Can modify prices',
                    help='If checked all users can modify the price of this product in a sale order or invoice.'),
    }
    
    _defaults = {
        'can_modify_prices': False,
    }

    def onchange_list_price(self, cr, uid, ids, list_price, uos_coeff, context=None):
        return {'value': {'list_price_copy': list_price}}

    def fields_get(self, cr, uid, allfields=None, context=None):
        if not context:
            context = {}
        group_obj = self.pool['res.groups']
        if group_obj.user_in_group(cr, uid, uid, 'dt_price_security.can_modify_prices', context=context):
            context['can_modify_prices'] = True
        else:
            context['can_modify_prices'] = False
      
        ret = super(product_product, self).fields_get(cr, uid, allfields=allfields, context=context)
      
        if group_obj.user_in_group(cr, uid, uid, 'dt_price_security.can_modify_prices', context=context):
            if 'list_price_copy' in ret:
                ret['list_price_copy']['invisible'] = True
        else:
            if 'list_price' in ret:
                ret['list_price']['invisible'] = True
      
        if group_obj.user_in_group(cr, uid, uid, 'dt_price_security.hide_purchase_prices', context=context):
            if 'standard_price' in ret:
                ret['standard_price']['invisible'] = True
            if 'cost_method' in ret:
                ret['cost_method']['invisible'] = True

        if not group_obj.user_in_group(cr, uid, uid, 'dt_price_security.modify_warehouse_price', context=context):
            if 'standard_price' in ret:
                ret['standard_price']['readonly'] = True
            if 'cost_method' in ret:
                ret['cost_method']['readonly'] = True

        return ret

    def write(self, cr, uid, ids, vals, context=None):
        if 'list_price' in vals:
            group_obj = self.pool['res.groups']

            if not group_obj.user_in_group(cr, uid, uid, 'dt_price_security.can_modify_prices', context=context):
                title = _('Violation of permissions')
                message = _('You do not have the necessary permissions to modify the price of the products')
                raise orm.except_orm(title, message)
        return super(product_product, self).write(cr, uid, ids, vals, context=context)
        

