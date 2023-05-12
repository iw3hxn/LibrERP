# -*- encoding: utf-8 -*-
##############################################################################

from openerp.osv import orm, fields


class AccountAccount(orm.Model):
    _inherit = 'account.account'

    _columns = {
        'external_code': fields.char('Codice Esterno', size=64, required=True, select=1),
    }
