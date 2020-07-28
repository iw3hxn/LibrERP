# -*- encoding: utf-8 -*-

from openerp.osv import fields, osv


class mrp_routing_workcenter(osv.Model):
    _inherit = "mrp.routing.workcenter"

    def _get_cost_efficiency(self, cr, uid, ids, context):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = line.cost_efficiency
        return res

    def _workcenter_total_cost(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for wline in self.browse(cr, uid, ids, context):
            wc = wline.workcenter_id
            cycle = wline.cycle_nbr
            # hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) * (wc.time_efficiency or 1.0)
            #  float(wc_use.hour_nbr*mult + ((wc.time_start or 0.0)+(wc.time_stop or 0.0)+cycle*(wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
            cost_efficiency = wline._get_cost_efficiency()[wline.id]
            cost = (wc.costs_cycle * cycle + wc.costs_hour * (wline.hour_nbr + (wc.time_start or 0.0) + (wc.time_stop or 0.0))) * (wc.time_efficiency or 1.0)
            # cost = line['hour_nbr'] * line['costs_hour'] * line['cycle_nbr']
            res[wline['id']] = cost * cost_efficiency
        return res

    _columns = {
        'cost_efficiency': fields.float("Cost Efficiency"),
        'costs_cycle': fields.related('workcenter_id', 'costs_cycle', required=True, string='Cost per cycle',  type='float'),
        'costs_hour': fields.related('workcenter_id', 'costs_hour', required=True, string='Cost per hour',  type='float'),
        'total_cost': fields.function(_workcenter_total_cost, method=True, type='float',
                                       string='Total Cost', store=False),
    }

    _defaults = {
        'cost_efficiency': 1
    }


