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
                partner_ids = self.pool['res.partner'].search(cr, uid, [('name', '=', partner_name)], context=context)
                result[product.id] = partner_ids[0]
            else:
                result[product.id] = product.seller_ids and product.seller_ids[0].name.id or ''
        return result

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
    }

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
        res = super(product_product, self).name_search(cr, uid, name, args, operator, context, limit)
        ids_supplier = self.search(
            cr, uid, args + [('supplier_code', operator, name)], limit=limit, context=context)

        ids = res + ids_supplier
        ids = list(set(ids))
        return ids
