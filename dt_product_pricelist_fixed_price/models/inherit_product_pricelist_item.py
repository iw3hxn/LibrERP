# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
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
from openerp.osv import orm, fields
from tools.translate import _
import decimal_precision as dp


class product_pricelist_item(orm.Model):
    def _price_field_get(self, cr, uid, context=None):
        """
            (1, u'Public Price'), 
            (2, u'Cost Price'), 
            (-1, u'Other Pricelist'), 
            (-2, u'Partner section of the product form'), 
            (-3, u'Fixed Price')
        """
        
        result = super(product_pricelist_item, self)._price_field_get(cr, uid, context)
        result.append((-3, _('Fixed Price')))
        return result

    _inherit = "product.pricelist.item"

    _columns = {
        'fixed_price': fields.float('Fixed Price',
            digits_compute=dp.get_precision('Sale Price')),
        'base': fields.selection(_price_field_get, 'Based on', required=True, size=-1, help="The mode for computing the price for this rule."),
        'string_discount': fields.char("String Discount", size=20, required=False, translate=False,
                                       help="Insert the multiple discount like: 50+10+5")
    }

    # def Calcolo_Sconto(self, cr, uid, ids, value, context=None):
    #     if value:
    #         discount_value = value.split("+")
    #         discount = float(100)
    #         for discount_str in discount_value:
    #             if discount_str != "+":
    #                 discount -= (discount * float(discount_str) / 100)
    #         discount = ((100 - discount) * -1) / 100
    #     else:
    #         discount = 0
    #     return {'value': {'price_discount': discount}}

    @staticmethod
    def calcolo_sconto(string_discount, price_unit, price_unit_uos):
        discount = 0
        if string_discount:
            string_discount = string_discount.strip() or '0.0'
            discount_value = string_discount.replace(',', '.').split("+")
            discount = float(100)
            for discount_str in discount_value:
                if discount_str.strip().replace('.', '').isdigit():
                    discount -= (discount * float(discount_str) / 100)
            discount = 100 - discount

        price_unit_discount = price_unit * (100 - discount) / 100
        price_unit_discount_uos = price_unit_uos * (100 - discount) / 100

        return {'value': {
            'discount': discount,
            'string_discount': string_discount,
            'price_unit_discount': price_unit_discount,
            'price_unit_discount_uos': price_unit_discount_uos
        }}

    def Calcolo_Sconto(self, cr, uid, ids, string_discount, context=None):
        values = self.calcolo_sconto(string_discount, 0, 0)
        return {'value': {
            'price_discount': -1 * values['value']['discount'] / 100,
            # 'string_discount': values['value']['string_discount']
        }}
