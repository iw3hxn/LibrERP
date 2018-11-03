# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Didotech SRL
#    Copyright 2014 Didotech SRL
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


class res_company(orm.Model):

    _inherit = 'res.company'

    def write(self, cr, uid, ids, values, context={}):

        if not ids:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]

        res = super(res_company, self).write(cr, uid, ids, values, context=context)

        if values.get('currency_id', False):
            product_price_type_obj = self.pool['product.price.type']
            product_price_type_ids = product_price_type_obj.search(cr, uid, [], context=context)
            product_price_type_obj.write(cr, uid, product_price_type_ids, {'currency_id': values.get('currency_id')}, context=context)

        return res
