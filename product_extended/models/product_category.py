# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields
from openerp.tools.translate import _


class product_category(orm.Model):
    _inherit = 'product.category'

    def _have_product(self, cr, uid, ids, field_name, arg, context=None):
        if not len(ids):
            return []
        '''
        Show if have or not a bom
        '''
        context = context or self.pool['res.users'].context_get(cr, uid)

        product_obj = self.pool['product.template']

        res = {}
        ids = ids or []

        for category in self.browse(cr, uid, ids, context):
            bom_id = product_obj.search(cr, uid, [('categ_id', '=', category.id)], context=context)
            if bom_id:
                res[category.id] = True
            else:
                res[category.id] = False

        return res

    def _product_filter(self, cr, uid, obj, name, args, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not args:
            return []
        product_obj = self.pool['product.template']
        for search in args:
            if search[0] == 'have_product':
                if search[2]:
                    product_ids = product_obj.search(cr, uid, [], context=context)
                    if product_ids:
                        res = list(set([product.categ_id.id for product in product_obj.browse(cr, uid, product_ids, context)]))
                        return [('id', 'in', res)]
                    else:
                        return [('id', 'in', [])]
                else:
                    product_ids = product_obj.search(cr, uid, [], context=context)
                    if product_ids:
                        categ_ids = self.search(cr, uid, [('type', '!=', 'view')], context=context)
                        res = list(set([product.categ_id.id for product in product_obj.browse(cr, uid, product_ids, context)]))
                        return [('id', 'in', list(set(categ_ids)-set(res)))]
                    else:
                        return [('id', 'in', [])]

        return []

    _columns = {
        'have_product': fields.function(_have_product, fnct_search=_product_filter, method=True, type="boolean", string="Have Product"),
    }

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for category in self.browse(cr, uid, ids, context):
            if category.have_product:
                raise orm.except_orm(
                    _(u'Invalid action !'),
                    _(u'In order to delete a category {category}, it must be cancelled product!').format(category=category.complete_name))
        res = super(product_category, self).unlink(cr, uid, ids, context=context)
        return res
