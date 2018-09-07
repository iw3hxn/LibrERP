# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import decimal_precision as dp
from mrp import mrp_bom


class temp_mrp_routing(orm.Model):
    _name = 'temp.mrp.routing'
    _columns = {
        'mrp_routing_id': fields.many2one('mrp.routing', string='Routing', select=True),
        'name': fields.char('Name', size=128),
        # TODO Workcenter readonly SO FAR => Evaluate changeability in the future
        'workcenter_id': fields.many2one('mrp.workcenter', string='Workcenter', readonly=True),
        # 'workcenter_lines': fields.one2many('mrp.routing.workcenter', 'routing_id', 'Work Centers'),
        'user_ids': fields.many2many('res.users', string='Users', ondelete='cascade'),
        'user_id': fields.many2one('res.users', 'User', domain="[('id', 'in', user_ids[0][2])]"),
        'sequence': fields.integer('Sequence'),
        'cycle': fields.float('Cycle'),
        'hour': fields.float('Hour'),
        'row_color': fields.char('Row Color', store=False),
        'temp_mrp_bom_id': fields.many2one('temp.mrp.bom', 'Temp BoM', required=True, ondelete='cascade', select=True),
        'order_requirement_line_id': fields.many2one('order.requirement.line', 'Order requirement line',
                                                     required=True, ondelete='cascade', select=True)
    }

    _order = "sequence,id"
