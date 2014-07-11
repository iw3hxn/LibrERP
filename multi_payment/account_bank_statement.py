# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Didotech srl
#    (<http://www.didotech.com>). 
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
##############################################################################

from openerp.osv import orm, fields


class custom_account_bank_statement(orm.Model):
    _name = 'account.bank.statement'
    _inherit = 'account.bank.statement'

    def balance_check(self, cr, uid, st_id, journal_type='bank', context=None):
        st = self.browse(cr, uid, st_id, context=context)
        if st.balance_end_real != 0.0:
            super(custom_account_bank_statement, self).balance_check(cr, uid, st_id, journal_type='bank', context=context)
        return True
