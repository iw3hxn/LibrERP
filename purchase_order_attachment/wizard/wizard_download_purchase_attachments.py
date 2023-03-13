# -*- encoding: utf-8 -*-

import re
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import datetime
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class WizardDownloadPurchaseAttachments(orm.TransientModel):
    _name = "wizard.download.purchase.attachments"
    _description = 'Download products attachments'

    _columns = {
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 32, readonly=True),
        'state': fields.selection((
            ('choose', 'choose'),  # choose
            ('get', 'get'),  # get the file
        )),
    }

    _defaults = {
        'state': lambda *a: 'choose',
    }

    def download_attachment(self, cr, uid, ids, context=None):
        attachment_model = self.pool['ir.attachment']

        name = context.get('name', 'PO')
        file_name = u'{0}_{1}.zip'.format(name, datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))

        purchase_id = context.get('active_id', False)
        purchase = self.pool['purchase.order'].browse(cr, uid, purchase_id, context)

        product_ids = [line.product_id.id if line.product_id else False for line in purchase.order_line]

        attachment_ids = attachment_model.search(cr, uid, [
            ('res_model', '=', 'product.product'),
            ('res_id', 'in', product_ids),
        ], context=context)
        attachment_export_ids = []
        for attachment in attachment_model.browse(cr, uid, attachment_ids, context):
            name = attachment.name
            pattern = re.compile("\d{6}_[DSMBP]{1}_R\d{1,4}\..{1,}", re.IGNORECASE)

            if re.match(pattern, name):
                attachment_export_ids.append(attachment.id)

        out = attachment_model.get_as_zip(cr, uid, attachment_ids, log=True)
        return self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': file_name}, context=context)
