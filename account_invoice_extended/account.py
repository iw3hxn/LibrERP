# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp import pooler

class account_invoice(orm.Model):
    _inherit = 'account.invoice'
    
    def copy(self, cr, uid, order_id, defaults, context=None):
        defaults['user_id'] = uid
        return super(account_invoice, self).copy(cr, uid, order_id, defaults, context)


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    def get_precision_tax():
        def change_digit_tax(cr):
            res = pooler.get_pool(cr.dbname).get('decimal.precision').precision_get(cr, 1, 'Account')
            return (17, res+3)
        return change_digit_tax

    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute=get_precision_tax()),
    }