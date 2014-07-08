# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
#    Copyright (C) 2011 - TODAY Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields
from openerp.tools.translate import _
import decimal_precision as dp
import netsvc
import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import decimal_precision as dp


class res_company(orm.Model):
    _inherit = "res.company"
    _columns = {
        'property_repair_product': fields.property(
            'product.product',
            type='many2one',
            relation="product.product",
            string="Repair Generic Product",
            method=True,
            view_load=True,
        ),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True),
    }


class res_partner(orm.Model):
    _inherit = "res.partner"

    def _check_manufacturer(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for partner in self.read(cr, uid, ids, ['manufacturer']):
            product_ids = self.pool['product.product'].search(cr, uid, [('manufacturer', '=', partner['id'])])
            if len(product_ids) > 0:
                res[partner['id']] = True
            else:
                res[partner['id']] = False
        #print res
        return res

    _columns = {
        'manufacturer': fields.boolean("Manufacturer"),
        'is_manufacturer': fields.function(_check_manufacturer, type="boolean", method=True),
    }

    _defaults = {
        'manufacturer': lambda *a: False,
    }


class product_condition(orm.Model):
    _name = 'product.condition'
    _description = 'Product Condition'
    _columns = {
        'name': fields.char("Name", size=64, required=True),
    }
    _order = "name"


class repair_order(orm.Model):
    _name = 'repair.order'
    _description = 'Repair Order'

    def _get_contact_number(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for order in self.read(cr, uid, ids, ['customer_id', 'phone', 'cell_phone'], context=context):
            number = order['cell_phone'] and order['cell_phone'] or order['phone']
            if not number and order['customer_id']:
                partner = self.pool['res.partner'].read(cr, uid, order['customer_id'][0], ['phone'], context=context)
                if partner and partner.get('phone', False):
                    number = partner['phone']
            res[order['id']] = number or ''
        return res

    def _check_in_picking_done(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}.fromkeys(ids, False)
        if not len(ids):
            return res
        for order in self.read(cr, uid, ids, ['in_picking_id', 'state']):
            if order.get('in_picking_id', False):
                picking = self.pool['stock.picking'].read(cr, uid, order['in_picking_id'][0], ['state'], context=context)
                if picking and picking['state'] == 'done':
                    res[order['id']] = True
        return res

    def _check_out_picking2producer_done(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}.fromkeys(ids, False)
        if not len(ids):
            return res

        for order in self.read(cr, uid, ids, ['out_picking2producer_id', 'state']):
            if order.get('out_picking2producer_id', False):
                picking = self.pool['stock.picking'].read(cr, uid, order['out_picking2producer_id'][0], ['state'], context=context)
                if picking and picking['state'] == 'done':
                    res[order['id']] = True
        return res

    def _check_in_picking2producer_done(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}.fromkeys(ids, False)
        if not len(ids):
            return res
        for order in self.read(cr, uid, ids, ['in_picking_producer_id', 'state']):
            if order.get('in_picking_producer_id', False):
                picking = self.pool['stock.picking'].read(cr, uid, order['in_picking_producer_id'][0], ['state'], context=context)
                if picking and picking['state'] == 'done':
                    res[order['id']] = True
        return res

    def _check_picking_state(self, cr, uid, ids, context=None):
        order_ids = []
        stock = self.pool['stock.picking']
        for s in stock.read(cr, uid, ids, ['state'], context=context):
            if s['state'] and s['state'] == 'done':
                stock_order_ids = self.pool['repair.order'].search(cr, uid, ['|', ('in_picking_id', '=', s['id']), '|', ('out_picking2producer_id', '=', s['id']), ('in_picking_producer_id', '=', s['id'])])
                order_ids += stock_order_ids
        return order_ids

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool['account.tax'].compute_all(cr, uid, line.tax_id, line.price_unit * (1 - (line.discount or 0.0) / 100.0), line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool['res.currency']
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.so_lines:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        res = []
        for order in self.pool['sale.order'].read(cr, uid, ids, ['repair_order_id'], context=context):
            if order.get('repair_order_id', False):
                res.append(order['repair_order_id'][0])
        return res

    def _get_order_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool['sale.order.line'].browse(cr, uid, ids, context=context):
            repair_order_id = None
            if line.repair_order_id or line.order_id.repair_order_id:
                if line.repair_order_id:
                    repair_order_id = line.repair_order_id.id
                elif line.order_id.repair_order_id:
                    repair_order_id = line.order_id.repair_order_id.id
                    self.pool['sale.order.line'].write(cr, uid, [line.id], {'repair_order_id': repair_order_id})
            if repair_order_id:
                result[repair_order_id] = True
        return result.keys()

    _columns = {
        'name': fields.char('Title', size=24, required=True),
        'customer_id': fields.many2one('res.partner', "Customer", required=True),
        'partner_address_id': fields.many2one("res.partner", "Customer Address"),
        'dest_address_id': fields.many2one("res.partner", "Customer Address"),
        'product_id': fields.many2one("product.product", "Product", required=True, domain="[('type', 'not in', ['service'] )]"),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'region': fields.many2one('res.region', string='Region'),
        'country_id': fields.many2one('res.country', 'Country'),
        'phone': fields.char('Home Phone', size=16),
        'cell_phone': fields.char('Mobile Phone', size=16),
        'contact_number': fields.function(_get_contact_number, type="char", method=True, size=16, store=True, string="Contact Number"),
        'email': fields.char('Personal Email', size=64),
        'manufacturer': fields.many2one("res.partner", "Manufacturer", domain="[('is_manufacturer', '=', True)]", required=True),
        'manufacturer_pname': fields.char("Product Name", size=128, required=True),
        'manufacturer_pref': fields.char("Product Number", size=128, required=True),
        'product_category': fields.many2one("product.category", "Category"),
        'repair_condition': fields.many2one("product.condition", "Condition"),
        'serial': fields.char("Serial No.", size=24),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('confirmed', 'Confirmed'),
            ('analyzing', 'Under Examination'),
            ('ready', 'Ready to Repair'),
            ('under_repair', 'Under Repair'),
            ('2binvoiced', 'To be Invoiced'),
            ('sending2manu', 'Waiting to deliver to Supplier'),
            ('wait_reception', 'Waiting to receive from Supplier'),
            ('wait_delivery', 'Waiting to deliver to Customer'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ], 'State', readonly=True),
        'order_move_id': fields.many2one('stock.move', 'Move', domain="[('location_dest_id.usage', '=', 'customer')]", readonly=True, states={'draft': [('readonly', False)]}),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', states={'confirmed': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]}),
        'location_id': fields.many2one('stock.location', 'Current Location', select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'deliver_bool': fields.boolean('Deliver', help="Check this box if you want to manage the delivery once the product is repaired. If cheked, it will create a picking with selected product. Note that you can select the locations in the Info tab, if you have the extended view."),
        'purchased_date': fields.date("Purchased Date"),
        'warranty_date': fields.date("Warranty Date"),
        'order_date': fields.date("Create Date"),
        'invoiced': fields.boolean('Invoiced', readonly=True),
        'repaired': fields.boolean('Repaired', readonly=True),
        'under_warranty': fields.boolean('Under Warranty'),
        'repairable': fields.boolean('Repairable', readonly=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', help='The pricelist comes from the selected partner, by default.'),
        'partner_invoice_id': fields.many2one('res.partner.address', 'Invoicing Address', domain="[('partner_id', '=', customer_id)]"),
        'invoice_method': fields.selection([
            ("none", "No Invoice"),
            ("b4repair", "Before Repair"),
            ("after_repair", "After Repair")
        ], "Invoice Method",
            select=True, required=True, states={'draft': [('readonly', False)]}, readonly=True, help='This field allow you to change the workflow of the repair order. If value selected is different from \'No Invoice\', it also allow you to select the pricelist and invoicing address.'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'picking_id': fields.many2one('stock.picking', 'Picking', readonly=True),
        'internal_notes': fields.text('Internal Notes'),
        'quotation_notes': fields.text('Quotation Notes'),
        'paid_by': fields.selection([('customer', 'Customer'), ('manufacturer', "Manufacturer")], "Paid By", select=True),
        'so_id': fields.many2one("sale.order", "Sale Order", ),
        'so_lines': fields.one2many('sale.order.line', 'repair_order_id', 'Order Lines', readonly=True, states={'analyzing': [('readonly', False)], '2binvoiced': [('readonly', False)]}),
        'invoice_ids': fields.related('so_id', "invoice_ids", type="many2many", relation="account.invoice", readonly=True, states={'draft': [('invisible', True)]}),
        'picking_ids': fields.related('so_id', "picking_ids", type="one2many", relation="stock.picking", readonly=True, states={'draft': [('invisible', True)]}),
        'po_id': fields.many2one("purchase.order", "Purchase Order", states={'draft': [('invisible', True)]}),
        'po_lines': fields.related('po_id', "order_line", type="one2many", relation="purchase.order.line", states={'draft': [('invisible', True)]}),
        'company_id': fields.many2one("res.company", "Company"),
        'in_picking_id': fields.many2one("stock.picking", "Reception"),
        'out_picking_id': fields.many2one("stock.picking", "Delivery"),
        'out_picking2producer_id': fields.many2one("stock.picking", "Delivery to Producer"),
        'in_picking_producer_id': fields.many2one("stock.picking", "Reception From Producer"),
        'inward_ok': fields.function(_check_in_picking_done, method=True, type="boolean", string="Inward ok ?",
                                     store={
                                         'stock.picking': (_check_picking_state, ['state'], 10),
                                     },
                                     ),
        'outward_producer_ok': fields.function(_check_out_picking2producer_done, method=True, type="boolean", string="Sent to Producer ?",
                                               store={
                                                   'stock.picking': (_check_picking_state, ['state'], 10),
                                               },
                                               ),
        'inward_producer_ok': fields.function(_check_in_picking2producer_done, method=True, type="boolean", string="Recived from Producer ?",
                                              store={
                                                  'stock.picking': (_check_picking_state, ['state'], 10),
                                              },
                                              ),
        'is_analized': fields.boolean("Study Ok", readonly=True),
        'is_delivered': fields.boolean("Deliver Ok", readonly=True),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Sale Price'), string='Untaxed Amount',
                                          store={
                                              'sale.order': (_get_order, ['order_line', 'amount_untaxed', 'amount_tax', 'amount_total'], 11),
                                              'sale.order.line': (_get_order_line, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                                          },
                                          multi='sums', help="The amount without tax."),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Sale Price'), string='Taxes',
                                      store={
                                          'sale.order': (_get_order, ['order_line', 'amount_untaxed', 'amount_tax', 'amount_total'], 11),
                                          'sale.order.line': (_get_order_line, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                                      },
                                      multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Sale Price'), string='Total',
                                        store={
                                            'sale.order': (_get_order, ['order_line', 'amount_untaxed', 'amount_tax', 'amount_total'], 11),
                                            'sale.order.line': (_get_order_line, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                                        },
                                        multi='sums', help="The total amount."),
        'description': fields.text('Problem', required=True),
        'customer_ref': fields.char('Customer Ref', size=24),
        'accessory_ids': fields.one2many("repair.order.accessory", "order_id", "Accessories")
    }

    def _default_product(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        if user.company_id and user.company_id.property_repair_product:
            return user.company_id.property_repair_product.id
        return None

    def _default_company(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool['res.company'].search(cr, uid, [('parent_id', '=', False)])[0]

    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool['ir.sequence'].get(cr, uid, 'repair.order'),
        'state': 'draft',
        'is_analized': False,
        'is_delivered': False,
        'repairable': True,
        'repaired': False,
        'invoiced': False,
        #'invoice_method': lambda *a: 'none',
        'invoice_method': 'after_repair',
        'paid_by': 'customer',
        'pricelist_id': lambda self, cr, uid, context: self.pool['product.pricelist'].search(cr, uid, [('type', '=', 'sale')])[0],
        'order_date': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
        'product_id': _default_product,
        'company_id': _default_company,
    }

    def create(self, cr, uid, values, context=None):
        if 'name' in values and not values['name']:
            del values['name']
        return super(repair_order, self).create(cr, uid, values, context)

    def copy(self, cr, uid, order_id, defaults, context=None):
        defaults['name'] = None
        return super(repair_order, self).copy(cr, uid, order_id, defaults, context)

    def on_change_city(self, cr, uid, ids, city):
        res = {'value': {}}
        if(city):
            city_id = self.pool['res.city'].search(cr, uid, [('name', '=', city.title())])
            if city_id:
                city_obj = self.pool['res.city'].browse(cr, uid, city_id[0])
                res = {'value': {
                    'province': city_obj.province_id.id,
                    'region': city_obj.region.id,
                    'zip': city_obj.zip,
                    'country_id': city_obj.region.country_id.id,
                    'city': city.title(),
                }}
        return res

    def on_change_address(self, cr, uid, ids, dest_address_id, street=None, street2=None, city=None, zip=None, region=None, country_id=None):
        res = {'value': {}}
        vals = {
            'street': street,
            'street2': street2,
        }
        city_vals = self.on_change_city(cr, uid, ids, city)
        vals.update(city_vals.get('value', {}))
        if dest_address_id:
            self.pool['res.partner.address'].write(cr, uid, [dest_address_id], vals)
        else:
            dest_address_id = self.pool['res.partner.address'].create(cr, uid, vals)
            vals.update({'dest_address_id': dest_address_id})
        res.update({'value': vals})
        return res

    def on_change_product(self, cr, uid, ids, product_id):
        res = {'value': {}}
        if product_id:
            vals = {}
            product = self.pool['product.product'].browse(cr, uid, product_id)
            vals.update(
                {
                    'manufacturer': product.manufacturer and product.manufacturer.id or False,
                    'manufacturer_pname': product.manufacturer_pname or product.name,
                    'manufacturer_pref': product.manufacturer_pref or product.default_code,
                    'product_category': product.categ_id and product.categ_id.id or False
                }
            )
            res.update({'value': vals})
        return res

    def on_change_move_id(self, cr, uid, ids, move_id, product_id=None, customer_id=None, order_date=None):
        res = {'value': {}}
        if move_id:
            vals = {}
            move = self.pool['stock.move'].browse(cr, uid, move_id)
            purchased_date = move.date or move.create_date
            order_date = order_date or datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
            last_warranty_date = datetime.datetime.strptime(purchased_date, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(months=int(move.product_id.warranty or 0))
            under_warranty = False
            if last_warranty_date.strftime(DEFAULT_SERVER_DATE_FORMAT) >= order_date:
                under_warranty = True

            vals.update({
                'purchased_date': purchased_date,
                'serial': move.prodlot_id and "/".join([move.prodlot_id.prefix, move.prodlot_id.name]) or False,
                'under_warranty': under_warranty,
            })

            if under_warranty:
                vals.update({'invoice_method': 'after_repair', 'paid_by': 'manufacturer'})
            if not product_id or product_id != move.product_id.id:
                vals.update({'product_id': move.product_id.id})
                product_updates = self.on_change_product(cr, uid, ids, move.product_id.id)
                vals.update(product_updates.get('value', {}))
            if not customer_id:
                vals.update({'customer_id': move.partner_id.id})
                customer_updates = self.on_change_customer(cr, uid, ids, move.partner_id.id)
                vals.update(customer_updates.get('value', {}))
            res.update({'value': vals})
        return res

    def on_change_under_warranty(self, cr, uid, ids, under_warranty):
        res = {'value': {}}
        vals = {}
        if under_warranty:
            vals.update({
                'invoice_method': 'after_repair', 'paid_by': 'manufacturer'
            })
        else:
            vals.update({'paid_by': 'customer'})
        res['value'] = vals
        return res

    def on_change_customer(self, cr, uid, ids, customer_id, dest_address_id=None):
        res = {'value': {}}
        if customer_id:
            vals = {}
            customer = self.pool['res.partner'].browse(cr, uid, customer_id)
            partner_address = self.pool['res.partner'].address_get(cr, uid, [customer_id], ['default', 'contact'])
            partner_address_id = partner_address['default'] and partner_address['default'] or partner_address.get('contact', False)
            if partner_address_id and not dest_address_id:
                partner_contact = self.pool['res.partner.address'].browse(cr, uid, partner_address_id)
                vals.update(
                    {
                        'partner_address_id': partner_address_id,
                        'street': partner_contact.street,
                        'street2': partner_contact.street2,
                        'zip': partner_contact.zip,
                        'city': partner_contact.city,
                        'region': partner_contact.region and partner_contact.region.id or False,
                        'country_id': partner_contact.country_id and partner_contact.country_id.id or False,
                        'phone': partner_contact.phone and partner_contact.phone or customer.phone,
                        'email': partner_contact.email and partner_contact.email or customer.email,
                    }
                )

            if not partner_address_id and not dest_address_id:
                vals.update(
                    {
                        'city': customer.city and customer.city or False,
                        'country_id': customer.country and customer.country.id or False,
                        'phone': customer.phone,
                        'email': customer.email,
                    }
                )
            res.update({'value': vals})
        return res

    def action_picking_create(self, cr, uid, ids, *args):
        picking_id = False
        for order in self.browse(cr, uid, ids):
            picking_id = None
            if order.in_picking_id:
                picking_id = order.in_picking_id.id
            else:
                loc_id = order.customer_id.property_stock_customer.id
                istate = 'none'
                pick_name = self.pool['ir.sequence'].get(cr, uid, 'stock.picking.in')
                picking_id = self.pool['stock.picking'].create(cr, uid, {
                    'name': pick_name,
                    'origin': order.name,
                    'type': 'in',
                    'address_id': order.dest_address_id.id or order.partner_address_id.id,
                    'invoice_state': istate,
                    'company_id': order.company_id.id,
                    'move_lines': [],
                })

                if order.product_id:
                    dest = order.warehouse_id and order.warehouse_id.lot_input_id.id or False
                    new_prodlot = None
                    if order.serial:
                        new_prodlot = self.pool['stock.production.lot'].create(cr, uid, {
                            'name': order.serial or '-',
                            'product_id': order.product_id.id,
                        })

                    move_vals = {
                        'name': order.name + ': ' + order.manufacturer_pname or '' + order.manufacturer_pref and "[%s]" % (order.manufacturer_pref) or '',
                        'product_id': order.product_id.id,
                        'product_qty': 1,
                        'product_uos_qty': 1,
                        'product_uom': order.product_id.uom_id.id,
                        'product_uos': order.product_id.uom_id.id,
                        'date': datetime.date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'date_expected': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'location_id': loc_id,
                        'location_dest_id': dest,
                        'picking_id': picking_id,
                        'state': 'draft',
                        'company_id': order.company_id.id,
                        'prodlot_id': new_prodlot,
                    }
                    move = self.pool['stock.move'].create(cr, uid, move_vals)
                    self.pool['stock.move'].action_confirm(cr, uid, [move])
                    self.pool['stock.move'].force_assign(cr, uid, [move])
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return picking_id

    def button_study(self, cr, uid, ids, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        for order in self.read(cr, uid, ids, context=context):
            message = _("The Repair order '%s' is going to study by %s.") % (order['name'], user.name)
            self.log(cr, uid, order['id'], message)
        return self.write(cr, uid, ids, {'state': 'study'})

    def button_confirm(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [order.id], {'state': 'confirmed'})
            message = _("The Repair order '%s' has been confirmed.") % (order.name)
            self.log(cr, uid, order.id, message)
            if order.in_picking_id:
                if order.in_picking_id.state != 'done':
                    return self.pool['stock.picking'].action_process(cr, uid, [order.in_picking_id.id], context=context)
            else:
                picking_id = self.action_picking_create(cr, uid, [order.id])
                if picking_id:
                    self.write(cr, uid, ids, {'in_picking_id': picking_id})
                    return self.pool['stock.picking'].action_process(cr, uid, [picking_id], context=context)
        return True

    #-FIXED
    def action_cancel_draft(self, cr, uid, ids, *args):
        """ Cancels repair order when it is in 'Draft' state.
        @param *arg: Arguments
        @return: True
        """
        #print "action_cancel_draft is called "
        if not len(ids):
            return False
        sale_obj = self.pool['sale.order']
        for repair in self.browse(cr, uid, ids):
            if repair.so_id:
                #so should be in draft state
                sale_obj.action_cancel_draft(cr, uid, [repair.so_id.id])
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_create(uid, 'repair.order', id, cr)
        return True

    #--Fixing
    def action_confirm(self, cr, uid, ids, *args):
        """ Repair order state is set to 'To be invoiced' when invoice method
        is 'Before repair' else state becomes 'Confirmed'.
        @param *arg: Arguments
        @return: True
        """
        #print "action_confirm is called "
        #wf_service = netsvc.LocalService("workflow")

        for o in self.browse(cr, uid, ids):
            #if o.so_id and o.so_id.state == 'draft':
            #    wf_service.trg_validate(uid, 'sale.order', o.so_id.id, 'repair_confirm', cr)
            if not o.in_picking_id:
                picking_id = self.action_picking_create(cr, uid, [o.id])
                if picking_id:
                    self.write(cr, uid, ids, {'in_picking_id': picking_id})
                    partial_id = self.pool['stock.partial.picking'].create(
                        cr, uid, {'date': datetime.date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=dict(active_ids=[picking_id], active_model='stock.picking'))
                    self.pool['stock.partial.picking'].do_partial(cr, uid, [partial_id], context=dict(active_ids=[picking_id], active_model='stock.picking'))

            self.log(cr, uid, o.id, _("The Repair order '%s' has been confirmed.") % (o.name))
            if o.is_analized:
                if (o.is_analized and o.invoice_method == 'b4repair' and not o.invoiced):
                    self.write(cr, uid, [o.id], {'state': '2binvoiced'})
                elif (o.is_analized and (o.invoice_method != 'b4repair' or o.invoiced) and not o.repairable and not o.outward_producer_ok):
                    self.write(cr, uid, [o.id], {'state': 'sending2manu'})
                else:
                    self.write(cr, uid, [o.id], {'state': 'confirmed'})
            else:
                self.write(cr, uid, [o.id], {'state': 'analyzing'})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels repair order.
        @return: True
        """
        #print "action_cancel is called"

        wf_service = netsvc.LocalService("workflow")
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.so_id:
                wf_service.trg_validate(uid, 'sale.order', repair.so_id.id, 'cancel', cr)
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def wkf_analyzing_end(self, cr, uid, ids, *args):
        #print "wkf_analyzing_end is called "
        return self.action_analyzing_end(cr, uid, ids)

    def action_analyzing_end(self, cr, uid, ids, group=False, context=None):
        res = {}
        for repair in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [repair.id], {'is_analized': True, 'state': 'draft'})
            res[repair.id] = True
        return res

    def action_send2supplier(self, cr, uid, ids, group=False, context=None):
        #print "action_send2supplier is called "
        #pdb.set_trace()
        res = {}
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.out_picking2producer_id and repair.out_picking2producer_id.state != 'done':
                partial_id = self.pool['stock.partial.picking'].create(
                    cr, uid, {}, context=dict(active_ids=[repair.out_picking2producer_id.id]))
                self.pool['stock.partial.picking'].do_partial(cr, uid, [partial_id], context=dict(active_ids=[repair.out_picking2producer_id.id]))
            res[repair.id] = True
        return res

    def action_reception(self, cr, uid, ids, group=False, context=None):
        #print "action_send2supplier is called "
        #pdb.set_trace()
        res = {}
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.in_picking_producer_id and repair.in_picking_producer_id.state != 'done':
                partial_id = self.pool['stock.partial.picking'].create(
                    cr, uid, {}, context=dict(active_ids=[repair.in_picking_producer_id.id]))
                self.pool['stock.partial.picking'].do_partial(cr, uid, [partial_id], context=dict(active_ids=[repair.in_picking_producer_id.id]))
            res[repair.id] = True
        return res

    def wkf_invoice_create(self, cr, uid, ids, *args):
        #print "wkf_invoice_create is called "
        return self.action_invoice_create(cr, uid, ids)

    def action_invoice_create(self, cr, uid, ids, group=False, context=None):
        """ Creates invoice(s) for repair order.
        @param group: It is set to true when group invoice is to be generated.
        @return: Invoice Ids.
        """
        #print "action_invoice_create is called "

        res = {}
        for repair in self.browse(cr, uid, ids, context=context):
            res[repair.id] = False
            if repair.state in ('draft', 'cancel') or repair.invoice_id:
                continue
            if repair.so_id.state == 'draft':
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'sale.order', repair.so_id.id, 'repair_confirm', cr)
                #wf_service.trg_validate(uid, 'sale.order', repair.so_id.id, 'order_confirm', cr)
                #wf_service.trg_validate(uid, 'sale.order', repair.so_id.id, 'order_validate', cr)

            # Create final invoice
            #comment = repair.quotation_notes
            #if (repair.invoice_method != 'none'):
            #    if not repair.customer_id.property_account_receivable:
            #        raise osv.except_osv(_('Error !'), _('No account defined for customer "%s".') % repair.customer_id.name )
            #    if not repair.so_id:
            #        raise osv.except_osv(_('Error !'), _('No Sale Order defined for repair Order "%s".') % repair.name )
            #    in_id = self.pool['sale.order').manual_invoice(cr, uid, [repair.so_id.id])
            #    invoice_id = in_id and in_id.get('res_id', False) or False
            #    res[repair.id] = invoice_id
            #    self.write(cr, uid, [repair.id], {'invoiced': True, 'invoice_id': invoice_id})
            if repair.invoice_method == 'b4repair':
                if not repair.repairable:
                    self.write(cr, uid, [repair.id], {'state': 'sending2manu'}, context=context)
                else:
                    self.write(cr, uid, [repair.id], {'state': 'ready'}, context=context)
            #if repair.invoice_method == 'after_repair':
            #    self.write(cr, uid, [repair.id], {'state': 'wait_delivery'}, context=context)
        return res

    def action_picking_create_reception(self, cr, uid, ids, context=None):
        #print "action_picking_create_reception is called "
        picking_id = False
        for order in self.browse(cr, uid, ids):
            if order.repairable:
                continue
            if order.out_picking2producer_id and order.out_picking2producer_id.state != 'done':
                raise osv.except_osv(_('Error !'), _('Delivery to Supplier/Producer is not done yet.'))

            picking_id = None
            if order.in_picking_producer_id:
                picking_id = order.in_picking_producer_id.id
            else:
                loc_id = order.out_picking2producer_id.address_id.partner_id.property_stock_supplier.id
                istate = 'none'
                pick_name = self.pool['ir.sequence'].get(cr, uid, 'stock.picking.in')
                picking_id = self.pool['stock.picking'].create(cr, uid, {
                    'name': pick_name,
                    'origin': order.name,
                    'type': 'out',
                    'address_id': order.out_picking2producer_id.address_id.id,
                    'invoice_state': istate,
                    'company_id': order.company_id.id,
                    'move_lines': [],
                })

                self.write(cr, uid, [order.id], {'in_picking_producer_id': picking_id, 'state': 'wait_reception'})

                if order.product_id:
                    dest = order.warehouse_id and order.warehouse_id.lot_input_id.id or False
                    new_prodlot = None
                    if order.in_picking_id:
                        move_lines = self.pool['stock.move'].search(cr, uid, [('picking_id', '=', order.in_picking_id.id), ('product_id', '=', order.product_id.id)])
                        if len(move_lines) > 0:
                            product_move = self.pool['stock.move'].browse(cr, uid, move_lines[0])
                            if product_move.prodlot_id:
                                new_prodlot = product_move.prodlot_id.id
                    move_vals = {
                        'name': order.name + ': ' + order.manufacturer_pname or '' + order.manufacturer_pref and "[%s]" % (order.manufacturer_pref) or '',
                        'product_id': order.product_id.id,
                        'product_qty': 1,
                        'product_uos_qty': 1,
                        'product_uom': order.product_id.uom_id.id,
                        'product_uos': order.product_id.uom_id.id,
                        'date': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'date_expected': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'location_id': loc_id,
                        'location_dest_id': dest,
                        'picking_id': picking_id,
                        'state': 'draft',
                        'company_id': order.company_id.id,
                        'prodlot_id': new_prodlot,
                    }
                    move = self.pool['stock.move'].create(cr, uid, move_vals)
                    self.pool['stock.move'].action_confirm(cr, uid, [move])
                    self.pool['stock.move'].force_assign(cr, uid, [move])
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return picking_id

    def action_picking_create_producer(self, cr, uid, ids, context=None):
        #print "action_picking_create_producer is called "
        picking_id = False
        for order in self.browse(cr, uid, ids):
            if order.repairable:
                continue
            picking_id = None
            if order.out_picking2producer_id:
                picking_id = order.out_picking2producer_id.id
            else:
                loc_id = order.manufacturer.property_stock_supplier.id
                istate = 'none'
                address_ids = self.pool['res.partner'].address_get(cr, uid, [order.manufacturer.id], ['default', 'delivery'])
                address_id = address_ids['delivery'] and address_ids['delivery'] or address_ids['default']
                pick_name = self.pool['ir.sequence'].get(cr, uid, 'stock.picking.out')
                picking_id = self.pool['stock.picking'].create(cr, uid, {
                    'name': pick_name,
                    'origin': order.name,
                    'type': 'out',
                    'address_id': address_id,
                    'invoice_state': istate,
                    'company_id': order.company_id.id,
                    'move_lines': [],
                })

                self.write(cr, uid, [order.id], {'out_picking2producer_id': picking_id, 'state': 'sending2manu'})

                if order.product_id:
                    source = order.location_id and order.location_id.id or (order.warehouse_id and order.warehouse_id.lot_input_id.id or False)
                    new_prodlot = None
                    if order.in_picking_id:
                        move_lines = self.pool['stock.move'].search(cr, uid, [('picking_id', '=', order.in_picking_id.id), ('product_id', '=', order.product_id.id)])
                        if len(move_lines) > 0:
                            product_move = self.pool['stock.move'].browse(cr, uid, move_lines[0])
                            if product_move.prodlot_id:
                                new_prodlot = product_move.prodlot_id.id
                    move_vals = {
                        'name': order.name + ': ' + order.manufacturer_pname or '' + order.manufacturer_pref and "[%s]" % (order.manufacturer_pref) or '',
                        'product_id': order.product_id.id,
                        'product_qty': 1,
                        'product_uos_qty': 1,
                        'product_uom': order.product_id.uom_id.id,
                        'product_uos': order.product_id.uom_id.id,
                        'date': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'date_expected': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'location_id': source,
                        'location_dest_id': loc_id,
                        'picking_id': picking_id,
                        'state': 'draft',
                        'company_id': order.company_id.id,
                        'prodlot_id': new_prodlot,
                    }
                    move = self.pool['stock.move'].create(cr, uid, move_vals)
                    self.pool['stock.move'].action_confirm(cr, uid, [move])
                    self.pool['stock.move'].force_assign(cr, uid, [move])
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return picking_id

    def action_repair_ready(self, cr, uid, ids, context=None):
        """ Writes repair order state to 'Ready'
        @return: True
        """
        #print "action_repair_ready is called "
        for repair in self.browse(cr, uid, ids, context=context):
            #self.pool['mrp.repair.line').write(cr, uid, [l.id for
            #        l in repair.operations], {'state': 'confirmed'}, context=context)
            self.write(cr, uid, [repair.id], {'state': 'ready'})
        return True

    def action_invoice_cancel(self, cr, uid, ids, context=None):
        """ Writes repair order state to 'Exception in invoice'
        @return: True
        """
        #print "action_invoice_cancel is called "
        self.write(cr, uid, ids, {'state': 'invoice_except'})
        return True

    def action_repair_start(self, cr, uid, ids, context=None):
        """ Writes repair order state to 'Under Repair'
        @return: True
        """
        return self.write(cr, uid, ids, {'state': 'under_repair'}, context=context)

    def action_invoice_end(self, cr, uid, ids, context=None):
        """ Writes repair order state to 'Ready' if invoice method is Before repair.
        @return: True
        """
        #print "action_invoice_end is called "
        repair_line = self.pool['mrp.repair.line']
        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            if (order.invoice_method == 'b4repair'):
                val['state'] = 'ready'
                repair_line.write(cr, uid, [l.id for
                                            l in order.operations], {'state': 'confirmed'}, context=context)

            self.write(cr, uid, [order.id], val, context=context)
        return True

    def action_repair_end(self, cr, uid, ids, context=None):
        """ Writes repair order state to 'To be invoiced' if invoice method is
        After repair else state is set to 'Ready'.
        @return: True
        """
        #print "action_repair_end is called "
        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            val['repaired'] = True
            if (not order.invoiced and order.invoice_method == 'after_repair'):
                val['state'] = '2binvoiced'
            elif (not order.invoiced and order.invoice_method == 'b4repair'):
                val['state'] = 'ready'

            self.write(cr, uid, [order.id], val)
        return True

    def wkf_repair_done(self, cr, uid, ids, *args):
        #print "wkf_repair_done is called "
        self.action_repair_done(cr, uid, ids)
        return True

    def action_repair_done(self, cr, uid, ids, context=None):
        """ Creates stock move and picking for repair order.
        @return: Picking ids.
        """
        res = {}

        self.write(cr, uid, ids, {'state': 'done'})
        return res


class sale_order(orm.Model):
    _inherit = 'sale.order'
    _columns = {
        'repair_order_id': fields.many2one("repair.order", "Repair Order"),
    }


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    _columns = {
        'is_free': fields.boolean("No Invoice"),
        'repair_order_id': fields.many2one("repair.order", "Repair Order"),
    }

    def on_change_is_free(self, cr, uid, ids, is_free):
        res = {'value': {}}
        if is_free:
            res['value'].update({
                'discount': 100.00,
            })
        else:
            res['value'].update({
                'discount': 0.0,
            })
        return res

    def _create_so_from_ro(self, cr, uid, repair_order_id, context=None):
        so_id = None
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        if not company.shop_id:
                raise orm.except_orm(_('Warning'), _('Please set repair shop'))
        if repair_order_id:
            rorder = self.pool['repair.order'].browse(cr, uid, repair_order_id, context=context)
            if rorder.so_id:
                return rorder.so_id.id
            shops = self.pool['sale.shop'].search(cr, uid, [])
            sale_order_params = {
                'shop_id': company.shop_id.id,
                'partner_id': rorder.customer_id.id,
                'pricelist_id': rorder.pricelist_id and rorder.pricelist_id.id or rorder.customer_id.property_product_pricelist.id,
                'partner_invoice_id': rorder.dest_address_id.id or rorder.partner_address_id.id,
                'partner_order_id': rorder.dest_address_id.id or rorder.partner_address_id.id,
                'partner_shipping_id': rorder.dest_address_id.id or rorder.partner_address_id.id,
                'date_order': rorder.order_date,
                'fiscal_position': rorder.customer_id.property_account_position and rorder.customer_id.property_account_position.id or False,
                'client_order_ref': rorder.name,
                'origin': rorder.name,
                'repair_order_id': repair_order_id,
            }
            so_id = self.pool['sale.order'].create(cr, uid, sale_order_params)
            self.pool['repair.order'].write(cr, uid, [repair_order_id], {'so_id': so_id}, context=context)
        return so_id

    def create(self, cr, uid, vals, context=None):
        if not vals.get("order_id") and vals.get('repair_order_id'):
            so_id = self._create_so_from_ro(cr, uid, vals.get('repair_order_id'), context=context)
            vals.update({'order_id': so_id})
        return super(sale_order_line, self).create(cr, uid, vals, context=context)


class product_accessory(orm.Model):
    _name = 'product.accessory'
    _description = 'Product Accessory'
    _columns = {
        'name': fields.char("Accessory", size=64, required=True),
    }

    _order = "name"


class repair_order_accessory(orm.Model):
    _name = 'repair.order.accessory'
    _description = 'Repair Order Accessory'
    _columns = {
        'accessory_id': fields.many2one("product.accessory", "Accessory", required=True),
        'order_id': fields.many2one("repair.order", "Repair Order"),
        'product_uom_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'serial': fields.char("Serial No.", size=64),
        "note": fields.text("Note")
    }
