# -*- coding: utf-8 -*-
# © 2019 Carlo Vettore - Didotech srl (www.didotech.com)

import logging

from openerp.osv import orm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class IrMailServer(orm.Model):
    _inherit = "ir.mail_server"

    def send_email(self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption='none', smtp_debug=False,
                   context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        company = user.company_id
        if company.email_node == company.local_node:
            return super(IrMailServer, self).send_email(cr, uid, message, mail_server_id, smtp_server, smtp_port, smtp_user, smtp_password, smtp_encryption, smtp_debug, context)
        else:
            _logger.error("Can't send email because my node configuration is different")
            return False

