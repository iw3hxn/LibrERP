# -*- encoding: utf-8 -*-


from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import datetime
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


# class PurchaseOrder(orm.TransientModel):
#     _inherit = "purchase.order"
#     _description = 'Download products attachments'
#
#     _columns = {
#         'product_zip_data_attachment': fields.binary(
#             string="File",
#             readonly=True
#         ),
#         'product_zip_data_attachment_name': fields.char('Filename', 32, readonly=True),
#     }
#
#     momentaneamente usiamo il wizard