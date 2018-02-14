# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import orm, fields


class CrmActivity(orm.Model):

    _name = 'crm.activity'
    _description = 'CRM Activity'
    _rec_name = 'name'
    _order = "sequence"

    _columns = {
        'name': fields.char('Name', required=True),
        'days': fields.integer('Number of days', default=0,
                          help='Number of days before executing the action, allowing you to plan the date of the action.'),
        'sequence': fields.integer('Sequence'),
    }

    _defaults = {
        'days': 0,
        'sequence': 10
    }
