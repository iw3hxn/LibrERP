# -*- coding: utf-8 -*-
# © 2014 - 2017 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _


class product_category(orm.Model):
    _inherit = 'product.category'

    def _have_product(self, cr, uid, ids, field_name, arg, context=None):
        if not len(ids):
            return []
        '''
        Show if category have or not a bom
        '''
        context = context or self.pool['res.users'].context_get(cr, uid)

        product_obj = self.pool['product.template']

        res = {}
        ids = ids or []

        for category in self.browse(cr, uid, ids, context):
            bom_id = product_obj.search(cr, uid, [('categ_id', '=', category.id)], context=context)
            res[category.id] = bom_id and True or False

        return res

    def _product_filter(self, cr, uid, obj, name, args, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not args:
            return []
        product_obj = self.pool['product.template']
        for search in args:
            if search[0] == 'have_product':
                product_ids = product_obj.search(cr, uid, [], context=context)
                if product_ids:
                    if search[2]:
                        res = list(
                            set([product.categ_id.id for product in product_obj.browse(cr, uid, product_ids, context)])
                        )
                        return [('id', 'in', res)]
                    else:
                        categ_ids = self.search(cr, uid, [('type', '!=', 'view')], context=context)
                        res = set([product.categ_id.id for product in product_obj.browse(cr, uid, product_ids, context)])
                        return [('id', 'in', list(set(categ_ids) - res))]
                else:
                    return [('id', 'in', [])]

        return []

    _columns = {
        'have_product': fields.function(
            _have_product, fnct_search=_product_filter, method=True, type="boolean", string="Have Product")
    }

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for category in self.browse(cr, uid, ids, context):
            if category.have_product:
                raise orm.except_orm(
                    _(u'Invalid action !'),
                    _(u'In order to delete a category {category}, it should contain no products!').format(category=category.complete_name))
        res = super(product_category, self).unlink(cr, uid, ids, context=context)
        return res
