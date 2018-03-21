# -*- encoding: utf-8 -*-

from openerp.osv import fields, osv


class mrp_routing_workcenter(osv.Model):
    _inherit = "mrp.routing.workcenter"

    def _workcenter_total_cost(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            cost = line.hour_nbr * line.costs_hour
            res[line.id] = cost
        return res

    _columns = {
        'costs_hour': fields.related('workcenter_id', 'costs_hour', required=True, string='Cost per hour',  type='float'),
        'total_cost': fields.function(_workcenter_total_cost, method=True, type='float',
                                       string='Total Cost', store=False),
    }


