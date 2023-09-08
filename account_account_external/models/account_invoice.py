# -*- encoding: utf-8 -*-
##############################################################################

import base64
import logging
import os

import tools

from openerp.osv import orm

_logger = logging.getLogger(__name__)
INVOICE_ROOT_PATH = tools.config.get('export_invoice_path', 'export_invoice')


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def cron_export_invoice_external_code(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        invoice_model = self.pool['account.invoice']
        export_pa_model = self.pool['wizard.export.fatturapa']
        attachment_model = self.pool['fatturapa.attachment.out']
        invoice_ids = invoice_model.search(cr, uid, [
            ('fatturapa_attachment_out_id', '=', False),
            ('state', 'in', ('open', 'paid')),
            ('type', 'in', ('in_invoice', 'in_refund'))
        ], context=context)
        if invoice_ids:
            for count, invoice in enumerate(invoice_model.browse(cr, uid, invoice_ids, context), start=1):
                _logger.info('cron_export_invoice_external_code {} / {}'.format(count, len(invoice_ids)))
                try:
                    context.update({
                        'type': invoice.type,
                        'active_ids': [invoice.id]
                    })
                    _logger.info("cron_export_invoice_external_code Export invoice {}".format(invoice.name))
                    res = export_pa_model.exportFatturaPA(cr, uid, [], context=context)
                    attachment_id = res.get('res_id')

                    if attachment_id:
                        attachment = attachment_model.browse(cr, uid, attachment_id, context)
                        store_fname = attachment.datas_fname
                        data = base64.decodestring(attachment.datas)
                        dpath = os.path.join(INVOICE_ROOT_PATH, cr.dbname)
                        path = os.path.join(dpath)
                        if not os.path.isdir(path):
                            _logger.debug("Create dirs: %s", path)
                            os.makedirs(path)
                        fname = os.path.join(path, store_fname)
                        fp = open(fname, 'wb')
                        try:
                            fp.write(data)
                        finally:
                            fp.close()
                        _logger.debug("Saved data to %s" % fname)
                    cr.commit()

                except Exception as e:
                    _logger.error("cron_export_invoice_external_code invoice {} ERRORE {}".format(invoice.name, e))

        return {
            'type': 'ir.actions.act_window_close',
        }
