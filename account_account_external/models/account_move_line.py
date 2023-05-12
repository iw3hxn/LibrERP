# -*- encoding: utf-8 -*-
##############################################################################

from openerp.osv import orm, fields


class AccountMoveLine(orm.Model):
    _inherit = 'account.move.line'

    _columns = {
        'external_code': fields.related(
            'account_id', 'external_code',
            type='char',
            string='Codice Esterno', size=64, required=True, select=1),
    }
