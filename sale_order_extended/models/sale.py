# -*- coding: utf-8 -*-
# © 2018-2019 Didotech srl (www.didotech.com)

from openerp.osv import orm
from utility import set_sequence
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def create(self, cr, uid, values, context=None):
        if 'order_line' in values:
            values['order_line'] = set_sequence(values['order_line'])
        return super(SaleOrder, self).create(cr, uid, values, context)

    def write(self, cr, uid, ids, values, context=None):
        if 'order_line' in values:
            values['order_line'] = set_sequence(values['order_line'])
        return super(SaleOrder, self).write(cr, uid, ids, values, context)
