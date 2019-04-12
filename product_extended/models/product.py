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


class product_template(orm.Model):
    _inherit = 'product.template'

    def __init__(self, registry, cr):
        """
            Add cost method "Last Purchase Price"
        """
        super(product_template, self).__init__(registry, cr)
        option = ('lpp', 'Last Purchase Price')

        type_selection = self._columns['cost_method'].selection
        if option not in type_selection:
            type_selection.append(option)


class product_product(orm.Model):
    _inherit = 'product.product'

    def _get_prefered_supplier(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for product in self.browse(cr, uid, ids, context):
            if context.get('partner_name', False):
                partner_name = context.get('partner_name')
                partner_ids = self.pool['res.partner'].search(cr, uid, [('name', '=', partner_name), ('supplier', '=', True)], context=context)
                if partner_ids:
                    result[product.id] = partner_ids[0]
                else:
                    result[product.id] = product.seller_ids and product.seller_ids[0].name.id or ''
            else:
                result[product.id] = product.seller_ids and product.seller_ids[0].name.id or ''
        return result

    def _get_stock_location_ids(self, cr, uid, ids, field_name, arg, context):
        res = {}
        stock_location_ids = self.pool['stock.location'].search(cr, uid, [('usage', '=', 'internal'),
                                                                          ('chained_location_type', '=', 'none')], context=context)
        for product_id in ids:
            res[product_id] = stock_location_ids
        return res

    _columns = {
        'prefered_supplier': fields.function(_get_prefered_supplier, type='many2one', relation='res.partner',
                                             string='Prefered Supplier'),
        'last_purchase_price': fields.float('Last purchase price', readonly=True),
        'last_purchase_date': fields.date('Last purchase date', readonly=True),
        'last_supplier_id': fields.many2one('res.partner', 'Last Supplier', readonly=True),
        'last_purchase_order_id': fields.many2one('purchase.order', 'Last Purchase Order', readonly=True),
        'last_sale_price': fields.float('Last sale price', readonly=True),
        'last_sale_date': fields.date('Last sale date', readonly=True),
        'last_customer_id': fields.many2one('res.partner', 'Last Customer', readonly=True),
        'last_sale_order_id': fields.many2one('sale.order', 'Last Sale Order', readonly=True),
        'last_customer_invoice_id': fields.many2one('account.invoice', 'Last Customer Invoice', readonly=True),
        'last_supplier_invoice_id': fields.many2one('account.invoice', 'Last Supplier Invoice', readonly=True),
        'supplier_id': fields.related('seller_ids', 'name', type='many2one', relation='res.partner',
                                     string='Supplier'),
        'supplier_code': fields.related('seller_ids', 'product_code', type='char', string="Supplier Code"),
        'stock_location_ids': fields.function(_get_stock_location_ids, type='one2many', relation='stock.location', string="Stock Locations", readonly=True)
    }

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'last_purchase_price': False,
            'last_purchase_date': False,
            'last_supplier_id': False,
            'last_purchase_order_id': False,
            'last_sale_price': False,
            'last_sale_date': False,
            'last_customer_id': False,
            'last_sale_order_id': False,
            'last_customer_invoice_id': False,
            'last_supplier_invoice_id': False,
            'stock_location_ids': False
        })
        return super(product_product, self).copy(cr, uid, id, default, context)

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if context.get('show_categ', False):
            for arg in args:
                if arg[0] == 'categ_id':
                    arg[1] = 'child_of'

        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

