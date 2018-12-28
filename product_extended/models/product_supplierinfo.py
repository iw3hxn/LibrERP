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
import logging
import time

import decimal_precision as dp
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class product_supplierinfo(orm.Model):
    _inherit = 'product.supplierinfo'

    _index_name = 'product_supplierinfo_name_index'

    def _auto_init(self, cr, context={}):
        super(product_supplierinfo, self)._auto_init(cr, context)
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s', (self._index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON product_supplierinfo (name)'.format(name=self._index_name))

    def _get_cost_price(self, cr, uid, ids, field_name, arg, context):
        result = {}
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        ctx = {
            'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        }
        for supplier_cost in self.browse(cr, uid, ids, context):
            pricelist = supplier_cost.name.property_product_pricelist_purchase
            if not pricelist:
                _logger.error(u'Missing pricelist for supplier {supplier}'.format(supplier=supplier_cost.name.name))
                result[supplier_cost.id] = 0.0
            else:
                price = self.pool['product.pricelist'].price_get(cr, uid, [pricelist.id], supplier_cost.product_id.id, 1, supplier_cost.name.id, context=ctx)[pricelist.id] or 0
                if pricelist:
                    from_currency = pricelist.currency_id.id
                    to_currency = user.company_id.currency_id.id
                    price_subtotal = self.pool['res.currency'].compute(
                        cr, uid, round=False,
                        from_currency_id=from_currency,
                        to_currency_id=to_currency,
                        from_amount=price,
                        context=context
                    )
                result[supplier_cost.id] = price_subtotal or price or 0.0
        return result

    def _last_order(self, cr, uid, ids, name, arg, context):
        res = {}
        for supinfo in self.browse(cr, uid, ids, context):
            cr.execute(
                "select po.id, max(po.date_approve) from purchase_order as po, purchase_order_line as line where po.id=line.order_id and line.product_id=%s and po.partner_id=%s and po.state in ('approved', 'done') group by po.id order by max desc",
                (supinfo.product_id.id, supinfo.name.id,))
            record = cr.fetchone()
            if record:
                res[supinfo.id] = record[0]
            else:
                res[supinfo.id] = False
        return res

    def _last_order_date(self, cr, uid, ids, name, arg, context):
        res = {}
        purchase_order_obj = self.pool['purchase.order']
        last_orders = self._last_order(cr, uid, ids, name, arg, context)
        dates = purchase_order_obj.read(cr, uid, list(set(filter(None, last_orders.values()))), ['date_approve'], context)
        for suppinfo in ids:
            date_approve = [x['date_approve'] for x in dates if x['id'] == last_orders[suppinfo]]
            if date_approve:
                res[suppinfo] = date_approve[0]
            else:
                res[suppinfo] = False
        return res

    _columns = {
        'cost_price': fields.function(_get_cost_price, type='float', string="Cost Price", digits_compute=dp.get_precision('Purchase Price')),
        'list_price': fields.related('pricelist_ids', 'price', type='float', string="Price", digits_compute=dp.get_precision('Purchase Price'), ),
        'last_order': fields.function(_last_order, type='many2one', obj='purchase.order', method=True,
                                      string='Last Order'),
        'last_order_date': fields.function(_last_order_date, type='date', method=True, string='Last Order date'),
    }

    _sql_constraints = [
        ('supplier_product_uniq', 'unique(name, product_id)', _('Supplier must be unique for product')),
    ]
