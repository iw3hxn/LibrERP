# -*- coding: utf-8 -*-
# © 2019 - Giovanni Monteverde - Didotech srl
# © 2019 - Trevisan Michele - Didotech srl
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#

from openerp.osv import fields, orm
# from account import _
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class NewInvoices(orm.Model):
    _inherit = 'account.invoice'

    def email_new_invoices(self, cr, uid, context=None):
        parameter_model = self.pool['ir.config_parameter']

        last_check = parameter_model.get_param(cr, uid, 'invoice_last_check')
        if not last_check:
            last_check = (datetime.now() - timedelta(days=30)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        eline_ids = self.pool['einvoice.line'].search(cr, uid, [
            ('create_date', '>', str(last_check))
        ])

        invoice_ids = [line.invoice_id.id for line in self.pool['einvoice.line'].browse(cr, uid, eline_ids, context) if
                       line.invoice_id]

        invoice_ids = list(set(invoice_ids))

        if invoice_ids:
            body = u'Nel giorno {} sono state ricevute le seguenti fatture:\n\n'.format(datetime.now().strftime('%d/%m/%Y'))

            # order invoices by date
            invoice_ids = self.pool['account.invoice'].search(cr, uid, [('id', 'in', invoice_ids)],
                                                              order='date_invoice')
            for invoice in self.pool['account.invoice'].browse(cr, uid, invoice_ids):
                body += u'''<p>Nome fornitore: <strong>{inv.partner_id.name}</strong></p>
                    <p>Numero fattura: {inv.supplier_invoice_number}</p>
                    <p>Data: {inv.date_invoice}</p>
                    <p>Importo: <strong>{inv.amount_total}</strong></p>
                    <p>Numero registrazione: {inv.number}</p><br>\n\n'''.format(inv=invoice)

            company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
            body += u'{company.name}'.format(company=company)
            mail_message = self.pool['mail.message']
            subject = u'Report importazione fatture elettroniche'
            email_from = parameter_model.get_param(cr, uid, 'email_einvoices_report_from').encode('utf-8')
            email_to = parameter_model.get_param(cr, uid, 'email_einvoices_report_send_to').encode('utf-8')
            mail_message.schedule_with_attach(cr, uid, email_from, [email_to], subject, body, subtype='html')

        parameter_model.set_param(
            cr, uid, 'invoice_last_check', datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT), context
        )
