# -*- coding: utf-8 -*-

import logging

from openerp.osv import orm, fields
from openerp.tools.config import config

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class MrpRouting(orm.Model):

    _inherit = 'mrp.routing'

    def _compute_total_cost(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for rounting in self.browse(cr, uid, ids, context):
            res[rounting.id] = {
                'total_cost': rounting.workcenter_lines and sum(rounting.workcenter_lines.mapped('total_cost')) or 0,
                'total_hour_nbr': rounting.workcenter_lines and sum(rounting.workcenter_lines.mapped('hour_nbr')) or 0,
            }
        return res

    _columns = {
        'total_cost': fields.function(
            _compute_total_cost,
            method=True,
            type='float',
            string='Total Cost',
            store=False,
            multi="line"
        ),
        'total_hour_nbr': fields.function(
            _compute_total_cost,
            method=True,
            type='float',
            string='Total Hour',
            store=False,
            multi="line"
        ),
    }
