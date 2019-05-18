# -*- coding: utf-8 -*-
#
# Copyright 2018    - Associazione Odoo Italia <https://www.odoo-italia.org>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import fields, orm


class ItalyAdeTaxNature(orm.Model):
    _name = 'italy.ade.tax.nature'
    _description = 'Tax Italian Nature'

    _sql_constraints = [('code',
                         'unique(code)',
                         'Code already exists!')]

    _columns = {
        'code': fields.char(string='Code',
                            size=2),
        'name': fields.char(string='Name'),
        'help': fields.text(string='Help'),
        'active': fields.boolean(string='Active')
    }
    _default = {
        'active': True
    }
