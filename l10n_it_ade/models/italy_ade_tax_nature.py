# -*- coding: utf-8 -*-
#
# Copyright 2018    - Associazione Odoo Italia <https://www.odoo-italia.org>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
# Copyright 2020 - Didotech s.r.l. <https://www.didotech.com>
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
        'code': fields.char(string='Code', size=4),
        'name': fields.char(string='Name'),
        'help': fields.text(string='Help'),
        'active': fields.boolean(string='Active')
    }
    _default = {
        'active': True
    }
    _order = 'code'

    def get_non_taxable_nature(self, cr, uid, context=None):
        nature_ids = self.search(cr, uid, [('active', '=', True)], context=context)
        return [
            (nature.code, "[{}] {}".format(nature.code, nature.name))
            for nature in self.browse(cr, uid, nature_ids, context=context)
        ]
