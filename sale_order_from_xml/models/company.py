# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class Company(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'order_import_auto_confirm': fields.boolean('Confirm automatically imported orders'),
        'order_import_path': fields.char('Path to Order XMLs', size=256)
    }
