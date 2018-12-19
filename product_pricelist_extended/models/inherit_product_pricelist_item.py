# -*- coding: utf-8 -*-
# © 2018 Didotech srl (www.didotech.com)

from openerp.tools.translate import _

import logging

from openerp.osv import orm, fields
from openerp.tools.config import config

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

ENABLE_CACHE = config.get('product_cache', False)
CACHE_TYPE = config.get('cache_type', 'dictionary')


class ProductPricelistItem(orm.Model):
    _inherit = 'product.pricelist.item'

    def __init__(self, cr, uid):
        super(ProductPricelistItem, self).__init__(cr, uid)

        if CACHE_TYPE == 'redis':
            try:
                from openerp.addons.core_extended.redis import Redis
                host = config.get('redis_host', 'localhost')

                self._name_get = Redis(host, database=cr.db_name, model=self._name)
            except:
                _logger.error("Unable to import Redis")
                from openerp.addons.core_extended.dict_cache import SimpleCache
                self._name_get = SimpleCache()
        else:
            from openerp.addons.core_extended.dict_cache import SimpleCache
            self._name_get = SimpleCache()

    def _pricelist_type_get(self, cr, uid, context=None):
        return self.pool['product.pricelist']._pricelist_type_get(cr, uid, context)

    _columns = {
        'partner_id': fields.related('price_version_id', 'pricelist_id', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
        'type': fields.related('price_version_id', 'pricelist_id', 'type', type='selection', selection=_pricelist_type_get, string='Pricelist Type')
    }

    def write(self, cr, uid, ids, vals, context=None):
        for id in ids:
            if int(id) in self._name_get:
                del self._name_get[int(id)]
        return super(ProductPricelistItem, self).write(cr, uid, ids, vals, context)

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        new_ids = []
        for id in ids:
            if id in self._name_get:
                res.append((id, self._name_get[id]))
            else:
                new_ids.append(id)
        if not new_ids:
            return res
        context = context or self.pool['res.users'].context_get(cr, uid)

        for rule in self.read(cr, uid, new_ids, ['product_id', 'categ_id', 'base', 'base_pricelist_id', 'string_discount', 'fixed_price'], context=context):
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
            self._name_get[id] = name
            res.append((rule['id'], name))
        _logger.debug('ProductPricelistItem - compute {0} from {1}'.format(len(new_ids), len(ids)))
        return res
