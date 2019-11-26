# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import decimal_precision as dp


class product_price_history(orm.Model):
    _name = 'product.price.history'
    _description = 'Product Price History'
    _rec_name = 'product_id'
    _order = 'date_to desc'

    _index_name = 'product_price_history_product_id_index'

    def _auto_init(self, cr, context={}):
        super(product_price_history, self)._auto_init(cr, context)
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s', (self._index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON product_price_history (product_id)'.format(name=self._index_name))

    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True),
        'date_to': fields.datetime('Date To', readonly=True, required=True),
        'product_id': fields.many2one('product.template', 'Product', readonly=True, required=True, ondelete='cascade', select=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True, required=True, ondelete='cascade'),
        'list_price': fields.float('Previous Sale Price', digits_compute=dp.get_precision('Sale Price'), readonly=True),
        'new_list_price': fields.float('New Sale Price', digits_compute=dp.get_precision('Sale Price'), readonly=True),
        'standard_price': fields.float('Previous Cost Price', digits_compute=dp.get_precision('Account'), readonly=True),
        'new_standard_price': fields.float('New Cost Price', digits_compute=dp.get_precision('Account'), readonly=True),
    }
