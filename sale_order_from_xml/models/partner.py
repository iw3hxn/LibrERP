# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class Partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'external_id': fields.integer('External ID', help="ID in external database")
    }
