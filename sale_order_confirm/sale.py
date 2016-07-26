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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import decimal_precision as dp
import re


class product_pricelist(orm.Model):
    _inherit = "product.pricelist"

    _columns = {
        'contract': fields.boolean('Contract', help="Set if this Pricelist not need approve on Sale order")
    }


class sale_order(orm.Model):
    _inherit = "sale.order"

    def service_only(self, cr, uid, ids, values, context):
        deleted_products = []
        service = True
        if values and 'order_line' in values and values['order_line']:
            for line in values['order_line']:
                # create new line
                if line[0] == 0:
                    if 'product_id' in line[2] and line[2]['product_id']:
                        product = self.pool['product.product'].browse(cr, uid, line[2]['product_id'], context)
                        if not product.type == 'service':
                            if line[0] == 0:
                                return False
                elif line[0] == 2 and line[1]:
                    order_line = self.pool['sale.order.line'].browse(cr, uid, line[1], context)
                    if order_line.product_id and not order_line.product_id.type == 'service':
                        deleted_products.append(order_line.product_id.id)
        elif not ids:
            return False
        else:
            service = False

        if ids:
            for order in self.browse(cr, uid, ids, context):
                if order.order_line:
                    for order_line in order.order_line:
                        if not order_line.product_id.type == 'service' and not order_line.product_id.id in deleted_products:
                            return False
                else:
                    if not service:
                        return False
        return True

    def hook_sale_state(self, cr, uid, orders, vals, context):
        print vals
        return True

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)

        if self.service_only(cr, uid, False, vals, context) and vals.get('order_policy', '') == 'picking':
            raise orm.except_orm(_('Warning'), _("You can't create an order with Invoicing being based on Picking if there are only service products"))

        ids = super(sale_order, self).create(cr, uid, vals, context=context)
        if vals.get('section_id', False) or vals.get('carrier_id', False) or vals.get('payment_term'):
            order = self.browse(cr, uid, ids, context)
            partner_vals = {}
            if not order.partner_id.section_id:
                partner_vals['section_id'] = vals.get('section_id')
            if not order.partner_id.property_delivery_carrier:
                partner_vals['property_delivery_carrier'] = vals.get('carrier_id')
            if not order.partner_id.property_payment_term:
                partner_vals['property_payment_term'] = vals.get('payment_term')
            if partner_vals:
                self.pool['res.partner'].write(cr, uid, [order.partner_id.id], partner_vals, context)
        return ids

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        orders = self.browse(cr, uid, ids, context)
        for order in orders:
            if self.service_only(cr, uid, ids, vals, context) and vals.get('order_policy', order.order_policy) == 'picking':
                raise orm.except_orm(_('Warning'), _("You can't create an order with Invoicing being based on Picking if there are only service products"))

        # adaptative function: the system learn
        if vals.get('section_id', False) or vals.get('carrier_id', False) or vals.get('payment_term'):
            for order in self.browse(cr, uid, ids, context):
                partner_vals = {}
                if not order.partner_id.section_id:
                    partner_vals['section_id'] = vals.get('section_id')
                if not order.partner_id.property_delivery_carrier:
                    partner_vals['property_delivery_carrier'] = vals.get('carrier_id')
                if not order.partner_id.property_payment_term:
                    partner_vals['property_payment_term'] = vals.get('payment_term')
                if partner_vals:
                    self.pool['res.partner'].write(cr, uid, [order.partner_id.id], partner_vals, context)

        if vals.get('state', False):
            self.hook_sale_state(cr, uid, orders, vals, context)

        return super(sale_order, self).write(cr, uid, ids, vals, context=context)

    def onchange_invoice_type_id(self, cr, uid, ids, invoice_type_id, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = {}
        if invoice_type_id:
            invoice_type_obj = self.pool['sale_journal.invoice.type']
            invoice_type = invoice_type_obj.browse(cr, uid, invoice_type_id, context)
            if invoice_type.invoicing_method == 'grouped':
                res['order_policy'] = 'picking'
        return {'value': res}

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        if res.get('value', False) and part:
            if not res['value'].get('property_account_position', False):
                company_id = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id.id
                company = self.pool['res.company'].browse(cr, uid, company_id, context)
                if company.default_property_account_position:
                    res['value']['fiscal_position'] = company.default_property_account_position and company.default_property_account_position.id
        return res

    def _credit_limit(self, cr, uid, ids, field_name, arg, context):
        res = dict.fromkeys(ids, 0.0)
        for order in self.browse(cr, uid, ids, context=context):

            if order.order_policy == 'prepaid':
                res[order.id] = 0
                continue
            partner = order.partner_id
            credit = partner.credit
            # We sum from all the sale orders that are aproved, the sale order lines that are not yet invoiced
            order_obj = self.pool['sale.order']
            approved_invoices_ids = order_obj.search(cr, uid, [('partner_id', '=', partner.id), ('state', 'not in', ['draft', 'cancel', 'done'])], context=context)
            approved_invoices_amount = 0.0
            for orders in order_obj.browse(cr, uid, approved_invoices_ids, context=context):
                for order_line in orders.order_line:
                    if not order_line.invoiced:
                        approved_invoices_amount += order_line.price_subtotal

            # We sum from all the invoices that are in draft the total amount
            invoice_obj = self.pool['account.invoice']
            draft_invoices_ids = invoice_obj.search(cr, uid, [('partner_id', '=', partner.id), ('state', '=', 'draft')], context=context)
            draft_invoices_amount = 0.0
            for invoice in invoice_obj.browse(cr, uid, draft_invoices_ids, context=context):
                draft_invoices_amount += invoice.amount_total
            available_credit = partner.credit_limit - credit - approved_invoices_amount - draft_invoices_amount

            res[order.id] = available_credit - order.amount_total
        return res

    def check_limit(self, cr, uid, ids, context=None):
        for processed_order in self.browse(cr, uid, ids, context=context):
            if processed_order.credit_limit < 0 and processed_order.company_id and processed_order.company_id.check_credit_limit:
                title = _('Credit Over Limit')
                msg = _('Is not possible to confirm because customer exceed the credit limit. \n Is Possible change the Order Policy \"Pay Before Delivery\" \n on tab \"Other Information\"')
                raise orm.except_orm(_(title), _(msg))
                return False
            if processed_order.visible_minimum and processed_order.sale_order_minimun > processed_order.amount_untaxed:
                if processed_order.shop_id.user_allow_minimun_id and processed_order.shop_id.user_allow_minimun_id.id == uid:  # if user can validate
                    return True
                title = _('Minimum Amount Billable')

                if processed_order.shop_id.user_allow_minimun_id:
                    msg = _('Is not possible to confirm because is not reached the minimum billable {amount} {currency} \n Only {user} can do it').format(amount=processed_order.sale_order_minimun, currency=processed_order.pricelist_id.currency_id.symbol, user=processed_order.shop_id.user_allow_minimun_id.name)
                else:
                    msg = _('Is not possible to confirm because is not reached the minimum billable {amount} {currency}').format(amount=processed_order.sale_order_minimun, currency=processed_order.pricelist_id.currency_id.symbol)

                raise orm.except_orm(_(title), _(msg))
                return False
        return True

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for sale in self.browse(cr, uid, ids, context=context):
            name = u'[{sale_name}] {partner_name}'.format(sale_name=sale.name, partner_name=sale.partner_id.name)
            res.append((sale.id, name))
        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=10):

        if not args:
            args = []
        if name:
            ids = self.search(cr, uid, [('name', '=', name)] + args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, uid, [('partner_id', 'ilike', name)] + args, limit=limit, context=context)
                ids = list(set(ids))
            if not len(ids):
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(
                        cr, uid, [('name', '=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)

        result = self.name_get(cr, uid, ids, context=context)
        return result

    _columns = {
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'credit_limit': fields.function(_credit_limit, string="Remaining Credit Limit", type='float', readonly=True, method=True),
        'sale_order_minimun': fields.related('shop_id', 'sale_order_minimun', type='float', string='Minimun Invoice', store=False, readonly=True),
        'visible_minimum': fields.related('shop_id', 'sale_order_have_minimum', type='boolean', string=_('Minimun Amount'), store=False, readonly=True),
        'visible_credit_limit': fields.related('company_id', 'check_credit_limit', type='boolean', string=_('Fido Residuo Visibile'), store=False, readonly=True),
        'validity': fields.date('Validity'),
        'state': fields.selection([
            ('draft', _('Quotation')),
            ('wait_technical_validation', _('Technical Validation')),
            ('wait_manager_validation', _('Manager Validation')),
            ('send_to_customer', _('Send To Customer')),
            ('wait_customer_validation', _('Customer Validation')),
            ('wait_supervisor_validation', _('Supervisor Validation')),
            ('waiting_date', _('Waiting Schedule')),
            ('manual', _('To Invoice')),
            ('progress', _('In Progress')),
            ('shipping_except', _('Shipping Exception')),
            ('invoice_except', _('Invoice Exception')),
            ('done', _('Done')),
            ('cancel', _('Cancelled'))
        ], 'Order State', readonly=True, help="Gives the state of the quotation or sales order. \nThe exception state is automatically set when a cancel operation occurs in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception). \nThe 'Waiting Schedule' state is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),
        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={
            'draft': [('readonly', False)],
            'wait_technical_validation': [('readonly', False)],
            'wait_manager_validation': [('readonly', False)]}
        ),
        'project_id': fields.many2one('account.analytic.account', 'Contract/Analytic Account', readonly=True, states={
            'draft': [('readonly', False)],
            'wait_technical_validation': [('readonly', False)],
            'wait_manager_validation': [('readonly', False)],
            'send_to_customer': [('readonly', False)],
            'wait_customer_validation': [('readonly', False)],
        }, help="The analytic account related to a sales order."),
        'required_tech_validation': fields.related('company_id', 'need_tech_validation', type='boolean', string=_('Required Technical Validation'), store=False, readonly=True),
        'need_tech_validation': fields.boolean("Technical Validation", readonly=True),
        'tech_validation': fields.boolean("Tech Validated ?", readonly=True),
        'required_manager_validation': fields.related('company_id', 'need_manager_validation', type='boolean', string=_('Required Manager Validation'), store=False, readonly=True),
        'need_manager_validation': fields.boolean("Manager Validation", readonly=True),
        'manager_validation': fields.boolean("Manager Validated ?", readonly=True),
        'email_sent_validation': fields.boolean("Email Sent to Customer ?", readonly=True),
        'customer_validation': fields.boolean("Customer Validated ?", readonly=True),
        # A validation after customer confirmation:
        'required_supervisor_validation': fields.related('company_id', 'need_supervisor_validation', type='boolean', string=_('Required Supervisor Validation'), store=False, readonly=True),
        'supervisor_validation': fields.boolean(_("Supervisor Validated?"), readonly=True),
        'product_id': fields.related('order_line', 'product_id', type='many2one', relation='product.product', string='Product'),
        'revision_note': fields.char('Reason', size=256, select=True),
        'last_revision_note': fields.related('sale_version_id', 'revision_note', type='char', string="Last Revision Note", store=True),
    }

    _defaults = {
        'need_tech_validation': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.need_tech_validation,
        'need_manager_validation': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.need_manager_validation,
        'required_tech_validation': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.need_tech_validation,
        'required_manager_validation': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.need_manager_validation,
        'required_supervisor_validation': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.need_supervisor_validation,
        'validity': lambda self, cr, uid, context: (datetime.today() + relativedelta(days=self.pool['res.users'].browse(cr, uid, uid, context).company_id.default_sale_order_validity or 0.0)).strftime(DEFAULT_SERVER_DATE_FORMAT),
    }

    def action_reopen(self, cr, uid, ids, context=None):
        result = super(sale_order, self).action_reopen(cr, uid, ids, context=context)

        for order in self.browse(cr, uid, ids, context):
            if order.state == 'draft':
                self.write(cr, uid, ids, {
                    'tech_validation': False,
                    'manager_validation': False,
                    'email_sent_validation': False,
                    'customer_validation': False,
                }, context)
        return result

    def check_direct_order_confirm(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            if order.state == 'draft' and order.pricelist_id and order.pricelist_id.contract:
                return True
            else:
                return False

    def check_tech_validation(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            if order.shop_id.user_tech_validation_id:
                if order.shop_id.user_tech_validation_id.id == uid:
                    return True
                else:
                    title = _('Technical Validation')
                    msg = _(u"It's not possible to confirm, for shop {shop} only user '{user}' can do it".format(shop=order.shop_id.name, user=order.shop_id.user_tech_validation_id.name))
                    raise orm.except_orm(_(title), _(msg))
                    return False

            else:
                return True

    def check_manager_validation(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            if order.shop_id.user_manager_validation_id:
                if order.shop_id.user_manager_validation_id.id == uid:
                    return True
                else:
                    title = _('Manager Validation')
                    msg = _(u"It's not possible to confirm, for shop {shop} only user '{user}' can do it".format(shop=order.shop_id.name, user=order.shop_id.user_manager_validation_id.name))
                    raise orm.except_orm(_(title), _(msg))
                    return False
            else:
                return True

    def check_supervisor_validation(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            if order.shop_id.user_supervisor_validation:
                if order.shop_id.user_supervisor_validation.id == uid:
                    return True
                else:
                    title = _('Supervisor Validation')
                    msg = _(u"It's not possible to confirm, for shop {shop} only user '{user}' can do it".format(shop=order.shop_id.name, user=order.shop_id.user_supervisor_validation.name))
                    raise orm.except_orm(_(title), _(msg))
                    return False
            else:
                return True

    def required_tech_validation(self, order):
        if order.company_id.tech_validation_if_no_product:
            for line in order.order_line:
                if not line.product_id:
                    order.write({'need_tech_validation': True})
                    return True
        return False

    def check_discount(self, order):
        if order.company_id.enable_discount_validation:
            max_discount = order.company_id.max_discount
            for line in order.order_line:
                if line.discount > max_discount:
                    order.write({'need_manager_validation': True})
                    return True
        return False

    def action_validate(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            if not order.partner_id.validate and order.company_id.enable_partner_validation:
                title = _('Partner To Validate')
                msg = _("It's not possible to confirm because customer must be validated")
                raise orm.except_orm(_(title), _(msg))
                return False

            if order.need_tech_validation and not order.tech_validation or self.required_tech_validation(order):
                vals = {
                    'state': 'wait_technical_validation',
                }
            elif self.check_discount(order):
                vals = {
                    'state': 'wait_manager_validation',
                }
            elif order.company_id.enable_margin_validation and order.amount_untaxed and (order.margin / order.amount_untaxed) * 100 < order.company_id.minimum_margin and not order.manager_validation:
                vals = {
                    'state': 'wait_manager_validation',
                }
            elif order.need_manager_validation and not order.manager_validation:
                vals = {
                    'state': 'wait_manager_validation',
                }
            elif not order.email_sent_validation:
                vals = {
                    'state': 'send_to_customer',
                }
            elif not order.customer_validation:
                vals = {
                    'state': 'wait_customer_validation',
                }
            elif order.required_supervisor_validation and not order.supervisor_validation:
                vals = {
                    'state': 'wait_supervisor_validation',
                }
            else:
                vals = {
                    'state': 'draft',
                    'tech_validation': False,
                    'manager_validation': False,
                    'customer_validation': False,
                    'email_sent_validation': False,
                    'supervisor_validation': False
                }
            order.write(vals)

        return True

    def check_validate(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            res = True

            if order.need_tech_validation and not order.tech_validation:
                res = False
            elif order.need_manager_validation and not order.manager_validation:
                res = False
            elif order.required_supervisor_validation and not order.supervisor_validation:
                res = False

            return res and order.email_sent_validation and order.customer_validation
        return True

    def check_direct_confirm(self, cr, uid, ids, context=None):
        if self.check_limit(cr, uid, ids, context):
            for order in self.browse(cr, uid, ids, context):
                values = {
                    'state': 'wait_customer_validation',
                    'customer_validation': True
                }
                if order.need_tech_validation:
                    values['tech_validation'] = True

                if (order.company_id.enable_margin_validation and order.amount_untaxed and (order.margin / order.amount_untaxed) < order.company_id.minimum_margin) or order.need_manager_validation:
                    values['manager_validation'] = True

                if order.required_supervisor_validation:
                    values['supervisor_validation'] = True

                self.write(cr, uid, [order.id], values, context)

            return self.action_validate(cr, uid, ids, context)
        else:
            return False

    def copy(self, cr, uid, ids, defaults, context=None):
        defaults.update(
            {
                'tech_validation': False,
                'manager_validation': False,
                'customer_validation': False,
                'email_sent_validation': False,
                'supervisor_validation': False
            }
        )
        defaults.update(self.default_get(cr, uid, ['order_policy', 'picking_policy', 'invoice_quantity'], context))
        return super(sale_order, self).copy(cr, uid, ids, defaults, context)


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    def _delivered_qty(self, cr, uid, ids, field_name, arg, context=None):
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

        if not context:
            context = {}
        res = {}
        # if line.order_id:
        #     context['warehouse'] = self.order_id.shop_id.warehouse_id.id

        for line in self.browse(cr, uid, ids, context):
            res[line.id] = {'qty_available': line.product_id and line.product_id.type != 'service' and line.product_id.qty_available or False,
                            'virtual_available': line.product_id and line.product_id.type != 'service' and line.product_id.virtual_available or False}
        return res

    # overwrite of a funcion inside sale_margin
    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product_id, qty=qty,
                                                             uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                                                             lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
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
        'order_id': fields.many2one('sale.order', 'Order Reference', ondelete='cascade', select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'readonly_price_unit': fields.related('order_id', 'company_id', 'readonly_price_unit', type='boolean', string=_('Readonly Price Unit'), store=False, readonly=True),
        'delivered_qty': fields.function(_delivered_qty, digits_compute=dp.get_precision('Product UoM'), string='Delivered Qty'),
        'qty_available': fields.function(_product_available, multi='qty_available',
                                         type='float', digits_compute=dp.get_precision('Product UoM'),
                                         string='Quantity On Hand'),
        'virtual_available': fields.function(_product_available, multi='qty_available',
                                             type='float', digits_compute=dp.get_precision('Product UoM'),
                                             string='Quantity Available'),
        'product_type': fields.char('Product type', size=64),
    }

    _defaults = {
        'readonly_price_unit': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.readonly_price_unit,
        'order_id': lambda self, cr, uid, context: context.get('default_sale_order', False) or False
    }
