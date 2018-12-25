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

from openerp.osv import orm, fields
from tools.translate import _

class users(orm.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    
    _columns = {
        'discount_restriction_ids': fields.one2many('price_security.discount_restriction', 'user_id',
                                                    string='Discount Restrictions'),
    }

    def create(self, cr, uid, vals, context=None):
        if not vals.get('discount_restriction_ids', False):
            vals['discount_restriction_ids'] = [(0, False, {'name': 'All', 'min_discount': 0, 'max_discount': 100})]
        return super(users, self).create(cr, uid, vals, context)


class discount_restriction(orm.Model):
    _name = 'price_security.discount_restriction'
    _description = 'Discount Restriction'
    
    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist'),
        'min_discount': fields.float('Min. Discount'),
        'max_discount': fields.float('Max. Discount'),
        'user_id': fields.many2one('res.users', 'User', required=True),
    }
    
    def check_discount_with_restriction(self, cr, uid, discount, pricelist_id, company_id, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid, context=context)
        restriction_id = self.get_restriction_id(cr, uid, uid, pricelist_id, context=context)
        
        group_obj = self.pool['res.groups']
        if not group_obj.user_in_group(cr, uid, uid, 'dt_price_security.can_modify_prices', context=context):
            title = _('Discount out of range')
            msg1 = _('The applied discount is out of range with respect to the allowed. The discount can be between %s and %s for the current price list.')
            msg2 = _('The applied discount is out of range with respect to the allowed. You cannot give any discount with the current price list.')
            
            if restriction_id:
                restriction = self.browse(cr, uid, restriction_id, context=context)
                if isinstance(restriction, list):
                    restriction = restriction[0]
                if discount < restriction.min_discount or discount > restriction.max_discount:
                        raise orm.except_orm(title, msg1 % (restriction.min_discount, restriction.max_discount))
            else:
                if not company_id:
                    company_id = self.pool['res.users']._get_company(cr, uid)
                company_max_discount = self.pool['res.company'].browse(cr, uid, company_id, context).max_discount
                if discount > company_max_discount:
                    if company_max_discount == 0.0:
                        raise orm.except_orm(title, msg2)
                    else:
                        raise orm.except_orm(title, msg1 % (0, company_max_discount))
        return True
    
    def get_restriction_id(self, cr, uid, user_id, pricelist_id, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid, context=context)
        filters = [('user_id', '=', user_id)]
        if pricelist_id:
            filters.append(('pricelist_id', '=', pricelist_id))
        restriction_id = self.search(cr, uid, filters, context=context)
        
        if not restriction_id:
            filters = [('user_id', '=', user_id), ('pricelist_id', '=', False)]
            restriction_id = self.search(cr, uid, filters, context=context)
        
        if not restriction_id:
            return False
        
        if isinstance(restriction_id, list):
            restriction_id = restriction_id[0]
        return restriction_id
