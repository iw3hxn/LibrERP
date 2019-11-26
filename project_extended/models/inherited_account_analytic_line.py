# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2016 Didotech Srl. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################.

from openerp.osv import orm, fields

import decimal_precision as dp


from tools.translate import _


class account_analytic_line(orm.Model):
    _inherit = 'account.analytic.line'

    def _debit_credit_bal_qtty(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.read(cr, uid, ids, ['amount'], context=context):
            amount = line['amount']
            res[line['id']] = {
                'debit': amount > 0 and amount or 0,
                'credit': amount < 0 and -amount or 0
            }
        return res

    _columns = {
        'debit': fields.function(_debit_credit_bal_qtty, type='float', string='Debit', multi='debit_credit_bal_qtty',
                                 digits_compute=dp.get_precision('Account')),
        'credit': fields.function(_debit_credit_bal_qtty, type='float', string='Credit', multi='debit_credit_bal_qtty',
                                  digits_compute=dp.get_precision('Account')),
    }