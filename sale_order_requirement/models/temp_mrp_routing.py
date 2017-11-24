# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import decimal_precision as dp
from mrp import mrp_bom


class temp_mrp_routing(orm.Model):
    _name = 'temp.mrp.routing'
    _columns = {
        'mrp_routing_id': fields.many2one('mrp.routing', string='Routing'),
        'name': fields.char('Name', size=64),
        'workcenter_id': fields.many2one('mrp.workcenter', string='Workcenter'),
        'user_ids': fields.many2many('res.users', string='Users'),
        'user_id': fields.many2one('res.users', 'User', domain="[('id', 'in', user_ids[0][2])]"),
        'sequence': fields.integer('Sequence'),
        'cycle': fields.float('Cycle'),
        'hour': fields.float('Hour'),
        'row_color': fields.char('Row Color', store=False),
        'temp_mrp_bom_id': fields.many2one('temp.mrp.bom', 'Temp BoM', required=True, ondelete='cascade'),
        'order_requirement_line_id': fields.many2one('order.requirement.line', 'Order requirement line',
                                                     required=True, ondelete='cascade')
    }
