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

import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def print_sale(self, cr, uid, ids, context):
        return self.pool['account.invoice'].print_report(cr, uid, ids, 'sale.report_sale_order', context)

    def _get_purchase_order(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        purchase_order_obj = self.pool['purchase.order']
        purchase_requisition_obj = self.pool['purchase.requisition']
        for order in self.browse(cr, uid, ids, context):
            name = order.name
            direct_purchase_order_ids = purchase_order_obj.search(cr, uid, [('origin', 'ilike', name)], context=context)
            tender_ids = purchase_requisition_obj.search(cr, uid, [('origin', 'ilike', name)], context=context)
            tender_puchase_order_ids = purchase_order_obj.search(cr, uid, [('requisition_id', 'in', tender_ids)], context=context)
            result[order.id] = direct_purchase_order_ids + tender_puchase_order_ids
        return result

    _columns = {
        'purchase_order_ids': fields.function(_get_purchase_order, string=_("Purchase Order"), type='one2many', method=True, relation='purchase.order')
    }
    
    def action_wait(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        bom_obj = self.pool['mrp.bom']
        for order in self.browse(cr, uid, ids, context=context):
            suppliers = {}
            for order_line in order.order_line:
                date_planned = datetime.strptime(order.date_order, DEFAULT_SERVER_DATE_FORMAT) + \
                    relativedelta(days=order_line.product_id.seller_delay or 0.0)
                if order_line.product_id.is_kit:
                    bom_ids = bom_obj.search(cr, uid, [('product_id', '=', order_line.product_id.id), ('bom_id', '=', False)], context=context)
                    if bom_ids:
                        boms = bom_obj.browse(cr, uid, bom_ids, context)
                        for bom in boms:
                            if bom.type == 'phantom':
                                if order_line.mrp_bom:
                                    for child_bom in order_line.mrp_bom:
                                        # At the moment we use main supplier:
                                        supplierinfo = self.pool['product.template']._get_main_product_supplier(cr, uid, child_bom.product_id, context)
                                        if not supplierinfo:
                                            continue
                                        res = self.pool['purchase.order.line'].onchange_product_id(cr, uid, ids, supplierinfo.name.property_product_pricelist_purchase.id, child_bom.product_id.id, child_bom.product_uom_qty or 1, child_bom.product_uom.id,
                                            supplierinfo.name.id, order_line.order_id.date_order, supplierinfo.name.property_account_position.id, date_planned.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                            child_bom.product_id.name or '', False, False, context)

                                        product_to_buy = res['value'].get('product_qty') - child_bom.product_id.virtual_available  # child_bom.product_uom_qty or 1,

                                        if product_to_buy <= 0:
                                            continue

                                        line_values = {
                                            'product_qty': product_to_buy,
                                            'product_uom': res['value'].get('product_uom'),  # child_bom.product_uom.id,
                                            'price_unit': res['value'].get('price_unit'),  # child_bom.product_id.standard_price,
                                            'discount': res['value'].get('discount'),
                                            'partner_id': supplierinfo.name.id,  # Supplier
                                            'name': res['value'].get('name'),  # child_bom.product_id.name or '',
                                            # 'date_planned': time.strftime(DEFAULT_SERVER_DATE_FORMAT),  # Where we can get it from?
                                            'date_planned': date_planned.strftime(
                                                DEFAULT_SERVER_DATE_FORMAT),
                                            'company_id': order_line.company_id.id,
                                            'product_id': child_bom.product_id.id,
                                            'account_analytic_id': order.project_id.id,  # This is not an error. Just a wrong variable name. project_id is account_analytic_id
                                            'taxes_id': [(6, 0, res['value'].get('taxes_id'))],
                                        }

                                        if supplierinfo.name.id in suppliers:
                                            suppliers[supplierinfo.name.id].append(line_values)
                                        else:
                                            suppliers[supplierinfo.name.id] = [line_values]

                                    break

                elif order_line.product_id and order_line.type == 'make_to_order' and order_line.supplier_id:

                    standard_price = order_line.product_id.standard_price
                    purchase_price = self.pool['res.currency'].compute(cr, uid, order.pricelist_id.currency_id.id, order_line.supplier_id.property_product_pricelist_purchase.currency_id.id, order_line.purchase_price, round=True, currency_rate_type_from=False, currency_rate_type_to=False, context=context)

                    res = self.pool['purchase.order.line'].onchange_product_id(cr, uid, ids, order_line.supplier_id.property_product_pricelist_purchase.id, order_line.product_id.id, order_line.product_uom_qty or 1, order_line.product_uom.id,
                        order_line.supplier_id.id, order_line.order_id.date_order, order_line.supplier_id.property_account_position.id, date_planned.strftime(DEFAULT_SERVER_DATE_FORMAT),
                        order_line.name, purchase_price or standard_price, order_line.notes, context)

                    product_to_buy = res['value'].get('product_qty') - order_line.product_id.qty_available  # child_bom.product_uom_qty or 1,

                    if product_to_buy <= 0:
                        continue

                    line_values = {
                        'product_uom': res['value'].get('product_uom'),  # order_line.product_uom.id,
                        'price_unit': res['value'].get('price_unit'),  # order_line.purchase_price or order_line.product_id.standard_price,
                        'discount': res['value'].get('discount'),  # order_line.extra_purchase_discount or 0.00,
                        'product_qty': product_to_buy,  # order_line.product_uom_qty or 1,
                        'partner_id': order_line.supplier_id.id,  # Supplier
                        'name': res['value'].get('name'),  # order_line.name or '',
                        'date_planned': date_planned.strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'company_id': order_line.company_id.id,
                        'product_id': order_line.product_id.id,
                        'account_analytic_id': order.project_id.id,  # This is not an error. Just a wrong variable name. project_id is account_analytic_id
                        'taxes_id': [(6, 0, res['value'].get('taxes_id'))],
                    }

                    if order_line.supplier_id.id in suppliers:
                        suppliers[order_line.supplier_id.id].append(line_values)
                    else:
                        suppliers[order_line.supplier_id.id] = [line_values]
                elif order_line.product_id and order_line.type == 'make_to_order':
                    line_values = {
                        'product_uom_id': order_line.product_uom.id,
                        'product_qty': order_line.product_uom_qty or 1,
                        'product_id': order_line.product_id.id,
                    }

                    if 'no_supplier' in suppliers:
                        suppliers['no_supplier'].append(line_values)
                    else:
                        suppliers['no_supplier'] = [line_values]

        if suppliers:
            purchase_order_obj = self.pool['purchase.order']
            purchase_requisition_obj = self.pool['purchase.requisition']
            location_id = order.shop_id.warehouse_id.lot_stock_id.id
            for supplier_id, order_lines in suppliers.iteritems():
                if supplier_id == 'no_supplier':
                    # Control if there are requesition requests in state 'draft'. If find any,
                    # use them, if not create new.
                    requisition_ids = purchase_requisition_obj.search(cr, uid, [('state', '=', 'draft'), ('origin', '=', order.name)], context=context)
                    if requisition_ids:
                        for line in order_lines:
                            line['requisition_id'] = requisition_ids[0]
                            self.pool['purchase.requisition.line'].create(cr, uid, line, context=context)
                        if order_lines:
                            requisition_order = purchase_requisition_obj.browse(cr, uid, requisition_ids[0], context=context)
                            purchase_requisition_obj.write(cr, uid, requisition_ids[0],
                                {
                                    'origin': requisition_order.origin + ' | ' + order.name,
                                }, context=context)
                            message = _("The Requisition order {name} has been updated.").format(name=requisition_order.name)
                            self.log(cr, uid, order.id, message)
                    else:
                        requisition_id = purchase_requisition_obj.create(cr, uid, {
                            'origin': order.name,
                            'exclusive': 'multiple',
                            'user_id': uid,
                            'line_ids': [(0, 0, val) for val in order_lines],
                        }, context=context)
                        if requisition_id:
                            message = _("The Requisition order has been created.")
                            self.log(cr, uid, order.id, message)
                else:
                    purchase_order_values = purchase_order_obj.onchange_partner_id(cr, uid, [], supplier_id)['value']

                    purchase_id = purchase_order_obj.create(cr, uid, {
                        'origin': order.name,
                        'shop_id': order.shop_id and order.shop_id.id,
                        'partner_id': supplier_id,
                        'partner_address_id': purchase_order_values['partner_address_id'],
                        'pricelist_id': purchase_order_values['pricelist_id'],
                        'order_line': [(0, 0, val) for val in order_lines],  # [(0,0,line)],
                        'fiscal_position': purchase_order_values['fiscal_position'],
                        'invoice_method': 'manual',
                        'location_id': location_id,
                        'payment_term': purchase_order_values['payment_term']
                    }, context=context)
                    if purchase_id:
                        message = _("The Purchase order has been created.")
                        self.log(cr, uid, order.id, message)

        return super(sale_order, self).action_wait(cr, uid, ids, context)

    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context.update(stop_procurement=True)
        return super(sale_order, self)._create_pickings_and_procurements(cr, uid, order, order_lines, picking_id, context)


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    def _get_supplier_ids(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        context = context or self.pool['res.users'].context_get(cr, uid)
        for line in self.browse(cr, uid, ids, context):
            product = line.product_id
            if product:
                # --find the supplier
                if product.seller_ids:
                    seller_ids = list(set([info.name.id for info in product.seller_ids]))
                else:
                    # If not suppliers found -> returns all of them
                    seller_ids = self.pool['res.partner'].search(cr, uid, [('supplier', '=', True)], context=context)
            else:
                seller_ids = []
            result[line.id] = seller_ids
        return result

    _columns = {
        'manufacturer_id': fields.many2one('res.partner', 'Manufacturer',),
        'manufacturer_pref': fields.char('Manufacturer Product Code', size=64),
        # 'supplier_ids': fields.many2many('res.partner', string='Suppliers', readonly=True),
        'supplier_ids': fields.function(_get_supplier_ids, string="Suppliers", type='many2many', method=True,
                                        relation='res.partner'),
        # 'supplier_id': fields.many2one('res.partner', string='Supplier'),
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain="[('id', 'in', supplier_ids[0][2])]"),
        'extra_purchase_discount': fields.float('Ex. Purchase Discount', digits=(16, 2)),
        'bom_ids': fields.one2many('sale.order.line.mrp.bom', 'order_id', 'BoM'),
        'product_brand_id': fields.related('product_id', 'product_tmpl_id', 'product_brand_id', type='many2one', relation='product.brand', string=_('Brand'), store=False)
    }

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if vals.get('product_id', False):
            product = self.pool['product.product'].browse(cr, uid, vals['product_id'], context=context)
            # onchange_vals = self.pool.get('sale.order.line').product_id_change(cr, uid, [], value['pricelist_id'], linevalue['product_id'], linevalue['product_uom_qty'],False, 0, False, '', value['partner_id'])['value']
            if product.manufacturer and product.manufacturer_pref:
                vals.update({
                    'manufacturer_id': product.manufacturer.id,
                    'manufacturer_pref': product.manufacturer_pref,
                })
        return super(sale_order_line, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if vals.get('product_id', False):
            product = self.pool['product.product'].browse(cr, uid, vals['product_id'], context)
            if product.manufacturer and product.manufacturer_pref:
                vals.update({
                    'manufacturer_id': product.manufacturer.id,
                    'manufacturer_pref': product.manufacturer_pref,
                })

        return super(sale_order_line, self).write(cr, uid, ids, vals, context=context)

    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,
                          supplier_id=False, extra_purchase_discount=0.0, auto_supplier=True, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        supplierinfo_obj = self.pool['product.supplierinfo']
        result_dict = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product_id, qty,
                                                                     uom, qty_uos, uos, name, partner_id,
                                                                     lang, update_tax, date_order, packaging, fiscal_position, flag)

        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context)
            if product.supply_method == 'buy' and product.procure_method == 'make_to_order':
                if product.manufacturer and product.manufacturer_pref:
                    result_dict['value'].update({
                        'manufacturer_id': product.manufacturer.id,
                        'manufacturer_pref': product.manufacturer_pref,
                    })

                if not supplier_id and auto_supplier:
                    # --find the supplier
                    supplier_info_ids = supplierinfo_obj.search(cr, uid, [('product_id', '=', product.product_tmpl_id.id)], order="sequence", context=context)
                    supplier_infos = supplierinfo_obj.browse(cr, uid, supplier_info_ids, context=context)
                    seller_ids = [info.name.id for info in supplier_infos]

                    if not seller_ids:
                        seller_ids = self.pool['res.partner'].search(cr, uid, [('supplier', '=', True)], context=context)

                    result_dict['value'].update({
                        'supplier_id': len(seller_ids) == 1 and seller_ids and seller_ids[0] or False,
                        'supplier_ids': seller_ids,
                    })

                if supplier_id:
                    supplier = self.pool['res.partner'].browse(cr, uid, supplier_id, context=context)
                    supplier_pricelist = supplier.property_product_pricelist_purchase and supplier.property_product_pricelist_purchase.id or False
                    if supplier_pricelist:
                        ctx = {
                            'date': date_order or time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                        }
                        price = self.pool['product.pricelist'].price_get(cr, uid, [supplier_pricelist], product_id, 1, context=ctx)[supplier_pricelist] or 0
                        if price:
                            order_pricelist_id = self.pool['product.pricelist'].browse(cr, uid, pricelist, context).currency_id.id
                            price = self.pool['res.currency'].compute(cr, uid,
                                                              supplier.property_product_pricelist_purchase.currency_id.id,
                                                              order_pricelist_id,
                                                              price, round=True, currency_rate_type_from=False,
                                                              currency_rate_type_to=False, context=context)
                            result_dict['value'].update({'purchase_price': price})
                result_dict['value'].update({'type': 'make_to_order'})

        else:
            result_dict['value'].update({
                'manufacturer_id': False,
                'manufacturer_pref': None,
            })
        if extra_purchase_discount and result_dict['value'].get('purchase_price', False):
                price = result_dict['value'].get('purchase_price', 0.0)
                price *= (1 - (extra_purchase_discount or 0.0) / 100.0)
                result_dict['value'].update({'purchase_price': price})
        return result_dict
