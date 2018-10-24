# -*- coding: utf-8 -*-
# © 2018 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _


class ProductPricelistItem(orm.Model):
    _inherit = 'product.pricelist.item'

    def _pricelist_type_get(self, cr, uid, context=None):
        return self.pool['product.pricelist']._pricelist_type_get(cr, uid, context)

    _columns = {
        'partner_id': fields.related('price_version_id', 'pricelist_id', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
        'type': fields.related('price_version_id', 'pricelist_id', 'type', type='selection', selection=_pricelist_type_get, string='Pricelist Type')
    }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        context = context or self.pool['res.users'].context_get(cr, uid)
        for rule in self.read(cr, uid, ids, ['product_id', 'categ_id', 'base', 'base_pricelist_id', 'string_discount', 'fixed_price'], context=context):
            name = u''
            product_name = rule['product_id'] and rule['product_id'][1]
            category_name = rule['categ_id'] and rule['categ_id'][1]
            if product_name:
                name = _('Prodotto ')
            elif category_name:
                name = _('Categoria ')

            if rule['base'] not in [-1]:
                name += dict(self.fields_get(cr, uid, allfields=['base'], context=context)['base']['selection'])[rule['base']] + u' '

            if rule['base_pricelist_id']:
                name += rule['base_pricelist_id'][1] + ' '

            if rule['string_discount']:
                name += u' con sconto {discount}'.format(discount=rule['string_discount'])

            res.append((rule['id'], name))
        return res
