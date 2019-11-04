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

import decimal_precision as dp
from openerp.osv import orm, fields


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        return super(sale_order_line, self)._amount_line(cr, uid, ids, field_name, arg, context)

    _columns = {
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Sale Price'), store={
                'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, [], 5),
        }),
    }
