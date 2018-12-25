# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyraght (c) 2013-2016 Didotech srl (<http://www.didotech.com>)
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

import decimal_precision as dp
from openerp.osv import orm, fields
from openerp.tools.translate import _


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        vals = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id, context)
        if vals:
            vals.update({'origin_document': '{table_name}, {line_id}'.format(table_name=line._table_name, line_id=line.id)})
        return vals

    def _delivered_qty(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            qty = 0

            for move in line.move_ids:
                if move.state == 'done':
                    qty += move.product_qty

            res[line.id] = qty
        return res

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        # if line.order_id:
        #     context['warehouse'] = self.order_id.shop_id.warehouse_id.id

        for line in self.browse(cr, uid, ids, context):
            res[line.id] = {
                'qty_available': line.product_id and line.product_id.type != 'service' and line.product_id.qty_available or False,
                'virtual_available': line.product_id and line.product_id.type != 'service' and line.product_id.virtual_available or False}
        return res

    # overwrite of a funcion inside sale_margin
    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
                          flag=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context.update(error_on_available=False)
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product_id, qty=qty,
                                                             uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                                                             partner_id=partner_id,
                                                             lang=lang, update_tax=update_tax, date_order=date_order,
                                                             packaging=packaging, fiscal_position=fiscal_position,
                                                             flag=flag, context=context)
        if not pricelist:
            return res

        frm_cur = self.pool['res.users'].browse(cr, uid, uid, context).company_id.currency_id.id
        to_cur = self.pool['product.pricelist'].browse(cr, uid, [pricelist], context)[0].currency_id.id
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context)
            price = self.pool['res.currency'].compute(cr, uid, frm_cur, to_cur, product.cost_price, round=False)
            res['value'].update({
                'purchase_price': price,
                'product_type': product.type
            })

        return res

    _columns = {
        'order_id': fields.many2one('sale.order', 'Order Reference', ondelete='cascade', select=True, readonly=True,
                                    states={'draft': [('readonly', False)]}),
        'readonly_price_unit': fields.related('order_id', 'company_id', 'readonly_price_unit', type='boolean',
                                              string=_('Readonly Price Unit'), store=False, readonly=True),
        'delivered_qty': fields.function(_delivered_qty, digits_compute=dp.get_precision('Product UoM'),
                                         string='Delivered Qty'),
        'qty_available': fields.function(_product_available, multi='qty_available',
                                         type='float', digits_compute=dp.get_precision('Product UoM'),
                                         string='Quantity On Hand'),
        'virtual_available': fields.function(_product_available, multi='qty_available',
                                             type='float', digits_compute=dp.get_precision('Product UoM'),
                                             string='Quantity Available'),
        'product_type': fields.char('Product type', size=64),
    }

    _defaults = {
        'readonly_price_unit': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid,
                                                                                            context).company_id.readonly_price_unit,
        'order_id': lambda self, cr, uid, context: context.get('default_sale_order', False) or False
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        """
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        res = super(sale_order_line, self).default_get(cr, uid, fields, context=context)
        if not res.get('tax_id', False):
            fpos_obj = self.pool['account.fiscal.position']
            product_default_get = self.pool['product.product'].default_get(cr, uid, ['taxes_id', 'uom_id'])
            taxes = product_default_get.get('taxes_id', False)
            if taxes:
                taxes = self.pool['account.tax'].browse(cr, uid, taxes, context)

                if context.get('fiscal_position', False):
                    fpos = fpos_obj.browse(cr, uid, context['fiscal_position'], context)
                    if taxes:
                        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
                    else:
                        tax_id = []
                else:
                    if taxes:
                        tax_id = [line.id for line in taxes]
                    else:
                        tax_id = []

                res.update({
                    'tax_id': [(6, 0, tax_id)],
                })
        uom_id = product_default_get.get('uom_id', False)
        if uom_id:
            res.update({
                    'product_uom': uom_id
            })
        return res
