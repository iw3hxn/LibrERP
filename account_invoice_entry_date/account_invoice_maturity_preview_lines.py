# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, orm


class account_invoice_maturity_preview_lines(orm.TransientModel):

    _name = 'account.invoice.maturity.preview.lines'

    def _get_void(self, cr, uid, ids, field_name, arg, context=None):
        return {}

    _columns = {
        'date': fields.function(_get_void,
                                  type="char", string="Date"),
        'amount': fields.function(_get_void,
                                  type="float", string="Amount"),
        'currency_name': fields.function(_get_void,
                                  type="char", string="Currency"),
        'pay_overv_date': fields.function(_get_void,
                                  type="char", string="Date"),
        'pay_overv_amount': fields.function(_get_void,
                                  type="float", string="Amount"),
        'pay_overv_currency': fields.function(_get_void,
                                  type="char", string="Currency"),
    }

