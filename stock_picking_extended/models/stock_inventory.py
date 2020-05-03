# -*- coding: utf-8 -*-

import logging

from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class StockInventory(orm.Model):
    _inherit = "stock.inventory"

    _columns = {
        'evaluation_mode': fields.selection([('default', 'Default Price'),
                                             ('average', 'Average from stock move')], 'Evaluation Mode', required=1)
    }

    _defaults = {
        'evaluation_mode': 'default'
    }
