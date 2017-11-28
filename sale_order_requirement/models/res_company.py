# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class res_company(orm.Model):

    _inherit = 'res.company'

    _columns = {
        'split_prouction_order': fields.boolean('Split Production order from order requirement')
    }

    _defaults = {
        'split_prouction_order': True
    }