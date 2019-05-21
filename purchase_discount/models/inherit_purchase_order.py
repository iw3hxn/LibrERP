# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012 Pexego Sistemas Informáticos (<http://tiny.be>).
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


class purchase_order(orm.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj = self.pool['res.currency']
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                for c in self.pool['account.tax'].compute_all(cr, uid, line.taxes_id, line.price_unit * (
                    1 - (line.discount or 0.0) / 100.0), line.product_qty, line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        return self.pool['purchase.order'].search(cr, uid, [('order_line', 'in', ids)], context=context)

    _columns = {
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Purchase Price'), string='Untaxed Amount',
            store={
                'purchse.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'purchase.order.line': (_get_order, ['product_id', 'price_unit', 'taxes_id', 'discount', 'product_qty'], 10),
            }, multi="sums", help="The amount without tax"),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Purchase Price'), string='Taxes',
            store={
                'purchse.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'purchase.order.line': (_get_order, ['product_id', 'price_unit', 'taxes_id', 'discount', 'product_qty'], 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Purchase Price'), string='Total',
            store={
                'purchse.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'purchase.order.line': (_get_order, ['product_id', 'price_unit', 'taxes_id', 'discount', 'product_qty'], 10),
            }, multi="sums", help="The total amount"),
    }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        res = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context=context)
        res.update({'discount': order_line.discount or 0.0,
                    'price_unit': order_line.price_unit, })
        return res

    def _get_do_merge_order_line_keys(self):
        res = super(purchase_order, self)._get_do_merge_order_line_keys()
        res.append('discount')
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

