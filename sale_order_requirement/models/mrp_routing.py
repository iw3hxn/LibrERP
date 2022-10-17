# -*- coding: utf-8 -*-

import logging

from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class MrpRouting(orm.Model):

    _inherit = 'mrp.routing'

    _columns = {
        'force_single_production_order': fields.boolean("Force Single MO", default=False)
    }
