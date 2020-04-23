# -*- coding: utf-8 -*-
# © 2017-2018 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.addons.warning.warning import WARNING_MESSAGE, WARNING_HELP
from openerp.osv import orm, fields


class ProductProduct(orm.Model):
    _inherit = 'product.product'
    _columns = {
        'mrp_bom_warn': fields.selection(WARNING_MESSAGE, 'Mrp Bom', help=WARNING_HELP, required=True),
        'mrp_bom_warn_msg': fields.text('Message for MRP BOM'),

    }

    _defaults = {
        'mrp_bom_warn': 'no-message'
    }
