# -*- coding: utf-8 -*-
from openerp.osv import orm, fields


class ProductProduct(orm.Model):

    _inherit = 'product.product'

    _columns = {
        'standard_service_time': fields.float(string="Standard Service Time")
    }

    _defaults = {
        'standard_service_time': 1
    }
