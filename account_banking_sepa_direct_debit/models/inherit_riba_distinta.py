# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class riba_distinta(orm.Model):
    _inherit = "riba.distinta"

    _columns = {
        'sdd': fields.related('config', 'sdd', string="SDD", type="boolean"),
    }

