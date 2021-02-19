# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def set_default_value(cr, pool):

    uid = SUPERUSER_ID
    context = pool['res.users'].context_get(cr, uid)
    user = pool['res.users'].browse(cr, uid, uid, context)
    split_mrp_production = user.company_id.split_mrp_production

    order_requirement_line_model = pool['order.requirement.line']

    order_requirement_line_ids = order_requirement_line_model.search(cr, uid, [], context=context)
    _logger.info("Start Update {0} split_mrp_production".format(len(order_requirement_line_ids)))
    order_requirement_line_model.write(cr, uid, order_requirement_line_ids, {'split_mrp_production': split_mrp_production}, context=context)

    return True
