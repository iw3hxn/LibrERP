# -*- coding: utf-8 -*-
# © 2013-2018 Didotech srl (info@didotech.com)

import logging

from openerp.osv import orm
from openerp.tools.config import config

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

ENABLE_CACHE = config.get('product_cache', False)
CACHE_TYPE = config.get('cache_type', 'dictionary')


class MrpRoutingWorkcenter(orm.Model):

    _inherit = 'mrp.routing.workcenter'

    def create(self, cr, uid, vals, context=None):
        res = super(MrpRoutingWorkcenter, self).create(cr, uid, vals, context)
        if ENABLE_CACHE:
            self.pool['product.product'].product_cost_cache.empty()
            _logger.info(u'_cost_price CREATE cache empty')
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(MrpRoutingWorkcenter, self).write(cr, uid, ids, vals, context)
        if ENABLE_CACHE:
            self.pool['product.product'].product_cost_cache.empty()
            _logger.info(u'_cost_price CREATE cache empty')
        return res

    def _get_cost_efficiency(self, cr, uid, ids, context):
        res = {}
        for line_id in ids:
            res[line_id] = 1
        return res
