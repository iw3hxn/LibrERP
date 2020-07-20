# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright © 2013-2019 Didotech srl (<http://www.didotech.com>)
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
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _get_shop_id(self, cr, uid, context):
        shop_ids = self.pool['sale.shop'].search(cr, uid, [], context=context, limit=1)
        return shop_ids and shop_ids[0] or False

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # sale_order_obj = self.pool['sale.order']
        # sale_order_line_obj = self.pool['sale.order.line']
        res = super(sale_order, self).default_get(cr, uid, fields, context=context)
        if not res.get('shop_id', False):
            res['shop_id'] = self._get_shop_id(cr, uid, context)
        if not res.get('section_id', False):
            section_ids = self.pool['crm.case.section'].search(cr, uid, [('user_id', '=', uid)], context=context)
            if section_ids:
                res['section_id'] = section_ids[0]

        company_id = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        days = 0
        if company_id.sale_order_validity_end_of_month:
            days = 31
        validity = (datetime.today() + relativedelta(days=company_id['default_sale_order_validity'] or 0.0) + relativedelta(day=days)).strftime(DEFAULT_SERVER_DATE_FORMAT)

        res.update({
            'need_tech_validation': company_id['need_tech_validation'],
            'need_manager_validation': company_id['need_manager_validation'],
            'skip_supervisor_validation_onstandard_product': company_id['skip_supervisor_validation_onstandard_product'],
            'required_tech_validation': company_id['need_tech_validation'],
            'required_manager_validation': company_id['need_manager_validation'],
            'required_supervisor_validation': company_id['need_supervisor_validation'],
            'validity': validity,
        })
        #
        return res

    def service_only(self, cr, uid, orders, context):
        service = True
        for order in orders:
            if order.order_line:
                for order_line in order.order_line:
                    if order_line.product_id and order_line.product_id.type != 'service':
                        return False
            elif not service:
                    return False
        return True

    def hook_sale_state(self, cr, uid, orders, vals, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # function call if change state the sale order
        return True

    def adaptative_function(self, cr, uid, orders, vals, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if vals.get('section_id', False) or vals.get('carrier_id', False) or vals.get('payment_term'):
            for order in orders:
                partner_vals = {}
                if not order.partner_id.section_id:
                    partner_vals['section_id'] = vals.get('section_id')
                if not order.partner_id.property_delivery_carrier:
                    partner_vals['property_delivery_carrier'] = vals.get('carrier_id')
                if not order.partner_id.property_payment_term:
                    partner_vals['property_payment_term'] = vals.get('payment_term')
                if partner_vals:
                    self.pool['res.partner'].write(cr, uid, [order.partner_id.id], partner_vals, context)
        return True

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        order_id = super(sale_order, self).create(cr, uid, vals, context=context)
        order = self.browse(cr, uid, order_id, context)
        self.adaptative_function(cr, uid, [order], vals, context)
        order_state = vals.get('state', order.state)
        if order_state:
            vals_copy = vals.copy()
            vals_copy['state'] = order_state
            self.hook_sale_state(cr, uid, [order], vals_copy, context)
        return order_id

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if vals:
            if not isinstance(ids, (list, tuple)):
                ids = [ids]

            orders = self.browse(cr, uid, ids, context)
            self.adaptative_function(cr, uid, orders, vals, context)
            if vals.get('state', False):
                self.hook_sale_state(cr, uid, orders, vals, context)

        return super(sale_order, self).write(cr, uid, ids, vals, context=context)

    def action_wait(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        company = self.pool['res.users'].browse(cr, uid, uid).company_id
        for order in self.browse(cr, uid, ids, context):
            if self.service_only(cr, uid, [order], context) and order.order_policy and order.order_policy == 'picking':
                if company.auto_order_policy:
                    order.write({'order_policy': 'manual'})
                else:
                    raise orm.except_orm(_('Warning'), _(
                        "You can't create an order with Invoicing being based on Picking if there are only service products"))
            else:
                if company.auto_order_policy:
                    default = self.default_get(cr, uid, ['order_policy'], context)
                    order.write({'order_policy': default.get('order_policy')})

        return super(sale_order, self).action_wait(cr, uid, ids, context)

    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
                'tech_validation': False,
                'manager_validation': False,
                'customer_validation': False,
                'email_sent_validation': False,
                'supervisor_validation': False,
        })
        super(sale_order, self).action_cancel_draft(cr, uid, ids, *args)
        return True

    def onchange_invoice_type_id(self, cr, uid, ids, invoice_type_id, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = {}
        if invoice_type_id:
            invoice_type_obj = self.pool['sale_journal.invoice.type']
            invoice_type = invoice_type_obj.read(cr, uid, invoice_type_id, ['invoicing_method'], context)
            if invoice_type['invoicing_method'] == 'grouped':
                res['order_policy'] = 'picking'
        return {'value': res}

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        if res.get('value', False) and part:
            if not res['value'].get('fiscal_position', False):
                company = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id
                if company.default_property_account_position:
                    res['value']['fiscal_position'] = company.default_property_account_position and company.default_property_account_position.id
        return res

    def _credit_limit(self, cr, uid, ids, field_name, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = dict.fromkeys(ids, 0.0)
        for order in self.browse(cr, uid, ids, context=context):

            if order.order_policy == 'prepaid':
                res[order.id] = 0
                continue
            partner = order.partner_id
            credit = partner.credit
            # We sum from all the sale orders that are aproved, the sale order lines that are not yet invoiced
            order_obj = self.pool['sale.order']
            order_line_obj = self.pool['sale.order.line']

            approved_order_ids = order_obj.search(cr, uid, [('partner_id', '=', partner.id), ('state', 'not in', ['draft', 'cancel', 'done'])], context=context)
            approved_order_line_ids = order_line_obj.search(cr, uid, [('invoiced', '=', False), ('order_id', 'in', approved_order_ids)], context=context)

            approved_invoices_amount = 0.0
            for order_line in order_line_obj.read(cr, uid, approved_order_line_ids, ['price_subtotal'], context=context):
                approved_invoices_amount += order_line['price_subtotal']

            # We sum from all the invoices that are in draft the total amount
            invoice_obj = self.pool['account.invoice']
            draft_invoices_ids = invoice_obj.search(cr, uid, [('partner_id', '=', partner.id), ('state', '=', 'draft')], context=context)
            draft_invoices_amount = 0.0
            for invoice in invoice_obj.browse(cr, uid, draft_invoices_ids, context=context):
                draft_invoices_amount += invoice.amount_total
            available_credit = partner.credit_limit - credit - approved_invoices_amount - draft_invoices_amount
            res[order.id] = available_credit - order.amount_total
        return res

    def partner_overdue_check(self, cr, uid, company, partner, context):
        # return True if there are same overdue payment
        account_move_line_obj = self.pool['account.move.line']
        overdue_date = (datetime.today() - relativedelta(days=company.date_max_overdue or 0.0)).strftime(DEFAULT_SERVER_DATE_FORMAT)

        account_move_ids = account_move_line_obj.search(cr, uid, [
            ('partner_id', '=', partner.id),
            ('account_id.type', 'in', ['receivable', 'payable']),
            ('stored_invoice_id', '!=', False),
            ('reconcile_id', '=', False),
            ('date_maturity', '<', overdue_date)], context=context)

        if account_move_ids:
            return True

        return False

    def check_limit(self, cr, uid, ids, context=None, orders=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        orders = orders or self.browse(cr, uid, ids, context=context)
        for order in orders:
            if order.credit_limit < 0 and order.company_id and order.company_id.check_credit_limit:
                title = _(u'Credit Over Limit')
                msg = _(u'Is not possible to confirm because customer exceed the credit limit. \n Is Possible change the Order Policy \"Pay Before Delivery\" \n on tab \"Other Information\"')
                raise orm.except_orm(_(title), _(msg))
                return False

            if order.visible_minimum and order.sale_order_minimun > order.amount_untaxed:
                if order.shop_id.user_allow_minimun_id and order.shop_id.user_allow_minimun_id.id == uid:  # if user can validate
                    return True
                # test if on line there are the product
                if order.shop_id.product_allow_minimun_id:
                    for line in order.order_line:
                        if line.product_id and line.product_id == order.shop_id.product_allow_minimun_id:
                            return True

                title = _(u'Minimum Amount Billable')
                if order.shop_id.user_allow_minimun_id:
                    msg = _(u'Is not possible to confirm because is not reached the minimum billable {amount} {currency} \n Only {user} can do it').format(amount=order.sale_order_minimun, currency=order.pricelist_id.currency_id.symbol, user=order.shop_id.user_allow_minimun_id.name)
                else:
                    msg = _(u'Is not possible to confirm because is not reached the minimum billable {amount} {currency}').format(amount=order.sale_order_minimun, currency=order.pricelist_id.currency_id.symbol)

                if order.shop_id.product_allow_minimun_id:
                    msg += _(u'\n\n or add the product \'{product}\'').format(product=order.shop_id.product_allow_minimun_id.name_get()[0][1])

                raise orm.except_orm(_(title), _(msg))
                return False

            if order.company_id and order.company_id.check_overdue:
                if self.partner_overdue_check(cr, uid, order.company_id, order.partner_id, context):
                    title = _(u'Overdue Limit')
                    msg = _(u'Is not possible to confirm because customer have a overdue payment')
                    raise orm.except_orm(_(title), _(msg))
                return False
        return True

    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not len(ids):
            return []
        res = []
        for sale in self.read(cr, uid, ids, ['id', 'name', 'partner_id'], context=context):
            name = u'[{sale_name}] {partner_name}'.format(sale_name=sale['name'], partner_name=sale['partner_id'][1])
            res.append((sale['id'], name))
        # for sale in self.browse(cr, uid, ids, context=context):
        #     name = u'[{sale_name}] {partner_name}'.format(sale_name=sale.name, partner_name=sale.partner_id.name)
        #     res.append((sale.id, name))

        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=10):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not args:
            args = []
        if name:
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
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

    def __init__(self, registry, cr):
        """
            Add state "Suspended"
        """
        super(sale_order, self).__init__(registry, cr)
        options = [('wait_technical_validation', _('Technical Validation')),
                   ('wait_manager_validation', _('Manager Validation')),
                   ('send_to_customer', _('Send To Customer')),
                   ('wait_customer_validation', _('Customer Validation')),
                   ('wait_supervisor_validation', _('Supervisor Validation'))]

        type_selection = self._columns['state'].selection
        for option in options:
            if option not in type_selection:
                type_selection.append(option)

    _columns = {
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'credit_limit': fields.function(_credit_limit, string="Remaining Credit Limit", type='float', readonly=True, method=True),
        'sale_order_minimun': fields.related('shop_id', 'sale_order_minimun', type='float', string='Minimun Invoice', store=False, readonly=True),
        'visible_minimum': fields.related('shop_id', 'sale_order_have_minimum', type='boolean', string=_('Minimun Amount'), store=False, readonly=True),
        'visible_credit_limit': fields.related('company_id', 'check_credit_limit', type='boolean', string=_('Fido Residuo Visibile'), store=False, readonly=True),
        'validity': fields.date('Validity'),
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
        'skip_supervisor_validation_onstandard_product': fields.related('company_id', 'skip_supervisor_validation_onstandard_product',
                                                                        type='boolean',
                                                                        string=_(
                                                                            'Skip Supervisor Verification if there are only standard product'),
                                                                        store=False,
                                                                        readonly=True),
        'supervisor_validation': fields.boolean(_("Supervisor Validated?"), readonly=True),
        'product_id': fields.related('order_line', 'product_id', type='many2one', relation='product.product', string='Product'),
        'revision_note': fields.char('Reason', size=256, select=True),
        'lost_reason_id': fields.many2one('crm.lost.reason', string='Lost Reason'),
        'last_revision_note': fields.related('sale_version_id', 'revision_note', type='char', string="Last Revision Note", store={
            'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['sale_version_id'], 20),
        }),
    }

    def action_reopen(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
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
        context = context or self.pool['res.users'].context_get(cr, uid)
        for order in self.browse(cr, uid, ids, context):
            if order.state == 'draft' and order.pricelist_id and order.pricelist_id.contract:
                return True
            else:
                return False

    def check_tech_validation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
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
        context = context or self.pool['res.users'].context_get(cr, uid)
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
        context = context or self.pool['res.users'].context_get(cr, uid)
        for order in self.browse(cr, uid, ids, context):
            if order.shop_id.user_supervisor_validation_id:
                if order.shop_id.user_supervisor_validation_id.id == uid:
                    return True
                else:
                    title = _('Supervisor Validation')
                    msg = _(u"It's not possible to confirm, for shop {shop} only user '{user}' can do it".format(shop=order.shop_id.name, user=order.shop_id.user_supervisor_validation_id.name))
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
                    _logger.info(u'Line have discount {discount} > {max_discount}'.format(discount=line.discount, max_discount=max_discount))
                    # order.write({'need_manager_validation': True})
                    return True
        return False

    def action_validate(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.button_dummy(cr, uid, ids, context=context)
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
            elif not order.manager_validation and self.check_discount(order):
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
        context = context or self.pool['res.users'].context_get(cr, uid)
        for order in self.browse(cr, uid, ids, context):
            res = True
            if order.need_tech_validation and not order.tech_validation:
                res = False
            elif order.need_manager_validation and not order.manager_validation:
                res = False
            elif order.required_supervisor_validation and not order.supervisor_validation:
                if order.skip_supervisor_validation_onstandard_product:
                    for line in order.order_line:
                        if line.product_id and line.product_id.is_kit:
                            return False
                    res = True
                else:
                    res = False
            return res and order.email_sent_validation and order.customer_validation
        return True

    def check_direct_confirm(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for order in self.browse(cr, uid, ids, context):
            if self.check_limit(cr, uid, ids, context, [order]):
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

    def copy(self, cr, uid, ids, default={}, context=None):
        default = default or {}
        context = context or self.pool['res.users'].context_get(cr, uid)
        company_id = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        days = 0
        if company_id.sale_order_validity_end_of_month:
            days = 31
        validity = (datetime.today() + relativedelta(
            days=company_id['default_sale_order_validity'] or 0.0) + relativedelta(day=days)).strftime(
            DEFAULT_SERVER_DATE_FORMAT)

        # For unknown reason default_get() returns more values than required
        default_values = self.default_get(cr, uid, ['order_policy', 'picking_policy', 'invoice_quantity'], context)
        default.update({
            'origin': False,
            'date_order': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
            'validity': validity,
            'tech_validation': False,
            'manager_validation': False,
            'customer_validation': False,
            'email_sent_validation': False,
            'supervisor_validation': False,
            'lost_reason_id': False,
            'order_policy': default_values['order_policy'],
            'picking_policy': default_values['picking_policy'],
            'invoice_quantity': default_values['invoice_quantity']
        })

        return super(sale_order, self).copy(cr, uid, ids, default, context=context)
