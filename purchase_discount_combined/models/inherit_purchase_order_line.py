# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012 Pexego Sistemas Informáticos (<http://tiny.be>).
#    Copyright (C) 2020 Didotech S.r.l. (<http://www.didotech.com/>).
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
import logging

from openerp.osv import orm, fields
import decimal_precision as dp

_logger = logging.getLogger(__name__)


class purchase_order_line(orm.Model):
    _inherit = "purchase.order.line"

    _columns = {
        'string_discount': fields.char(
            "String Discount", size=20, required=False, translate=False,
            help="Insert the multiple discount like: 50+10+5"),
    }

    _defaults = {
        'string_discount': '',
    }

    def _calcolo_sconto(self, string_discount):
        discount = 0
        if string_discount:
            string_discount = string_discount.strip() or '0.0'
            discount_value = string_discount.replace(',', '.').split("+")
            discount = float(100)
            for discount_str in discount_value:
                if discount_str.strip().replace('.', '').isdigit():
                    discount -= (discount * float(discount_str) / 100)
            discount = 100 - discount
        return {'value': {
            'discount': discount,
            'string_discount': string_discount,
        }}

    def Calcolo_Sconto(self, cr, uid, ids, string_discount, context=None):
        return self._calcolo_sconto(string_discount)


