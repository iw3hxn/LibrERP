# -*- coding: utf-8 -*-
# © 2019 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class ProjectTask(orm.Model):
    _inherit = 'project.task'

    # this is for not creating manufacture (create pickings but *NO* procurements)
    _columns = {
        'order_requirement_line_ids': fields.many2many('order.requirement.line', string='Order Requirement Lines',
                                                       readonly=True),
    }
