# -*- coding: utf-8 -*-
#
# Copyright 2020 - Didotech s.r.l. <https://www.didotech.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import fields, orm


class WithholdingType(orm.Model):
    # _position = []
    _name = "italy.ade.withholding.type"
    _description = 'FatturaPA Withholding Type'

    _sql_constraints = [('code',
                         'unique(code)',
                         'Code already exists!')]

    _columns = {
        'name': fields.char('Description', size=128),
        'code': fields.char('Code', size=4),
        'active': fields.boolean(string='Active')
    }
    _default = {
        'active': True
    }
    _order = 'code'
