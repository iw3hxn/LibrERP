# -*- coding: utf-8 -*-
# © 2018 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class AccountStatementImport(orm.TransientModel):

    _name = 'account.bank.statement.import'

    _description = 'Import account.bank.statement in .xls'

    _columns = {
        'template_id': fields.many2one('account.bank.statement.import.template', 'Formato Dati',
                                       required=True, readonly=False),
        # Data of file, in code BASE64
        'content_base64': fields.binary('File Path', required=False, translate=False),
        'file_name': fields.char('File Name', size=256),
    }
