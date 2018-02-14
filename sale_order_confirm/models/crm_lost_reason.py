# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
from tools import ustr
from tools.translate import _


class LostReason(orm.Model):
    _name = "crm.lost.reason"
    _description = 'Reason for loosing leads'

    _columns = {
        'name': fields.char('Name', required=True),
        'active': fields.boolean('Active', default=True)
    }

