# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from tools.translate import _

from addons.warning.warning import WARNING_MESSAGE, WARNING_HELP


class product_product(orm.Model):
    _inherit = 'product.product'
    _columns = {
        'mrp_bom_warn': fields.selection(WARNING_MESSAGE, 'Mrp Bom', help=WARNING_HELP, required=True),
        'mrp_bom_warn_msg': fields.text('Message for MRP BOM'),

    }

    _defaults = {
        'mrp_bom_warn': 'no-message'
    }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
