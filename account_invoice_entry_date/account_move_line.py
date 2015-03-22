# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 ISA srl (<http://www.isa.it>).
#    Copyright (C) 2013 Sergio Corato (<http://www.icstools.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import fields, orm
from tools.translate import _


class account_move_line(orm.Model):
    _inherit = 'account.move.line'
    
    def _maturity_amount(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            if 'maturity_currency' in field_names:
                res[line.id] = line.currency_id and line.currency_id.symbol or line.company_id and line.company_id.currency_id.symbol
            if 'maturity_debit' in field_names:
                res[line.id] = line.amount_currency or line.debit or ''
        return res
    
    _columns = {
        'maturity_currency': fields.function(
            _maturity_amount, type="char", store=False, string="Currency", method=True),
        'maturity_debit': fields.function(
            _maturity_amount, type="float", store=False, method=True)
    }