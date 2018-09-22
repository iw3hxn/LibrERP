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
        res = {}
        ids = ids or []

        cr.execute("select categ_id from product_template group by categ_id")
        record = [categ_id[0] for categ_id in cr.fetchall()]

        for category_id in ids:
            res[category_id] = category_id in record

        return res

    def _product_filter(self, cr, uid, obj, name, args, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not args:
            return []
        for search in args:
            if search[0] == 'have_product':
                cr.execute("select categ_id from product_template group by categ_id")
                record = [categ_id[0] for categ_id in cr.fetchall()]
                if record:
                    if search[2]:
                        res = list(set(record))
                        return [('id', 'in', res)]
                    else:
                        categ_ids = self.search(cr, uid, [('type', '!=', 'view')], context=context)
                        res = set(record)
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
