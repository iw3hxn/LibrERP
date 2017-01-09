# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012-2016 Didotech (<http://www.didotech.com>).
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

from openerp.osv import orm, fields
import time
import netsvc
import datetime
from dateutil.relativedelta import relativedelta
from tools.translate import _
import decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

import locale
locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool['account.tax']
        cur_obj = self.pool['res.currency']
        order_obj = self.pool['sale.order']
        res = {}
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            if line.order_id.have_subscription and line.product_id.subscription:
                k = order_obj.get_duration_in_months(line.order_id.order_duration) / order_obj.get_duration_in_months(line.product_id.order_duration)
                res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'] * k)
            else:
                res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    # Dangerous! Overwrites standard method
    def _product_margin(self, s2, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.product_id:
                if line.purchase_price:
                    purchase_price = line.purchase_price
                else:
                    purchase_price = line.product_id.standard_price

                if line.order_id.have_subscription and line.product_id.subscription:
                    price_subtotal = line.price_subtotal
                else:
                    price_subtotal = line.price_unit * line.product_uos_qty

                res[line.id] = round((price_subtotal * (100.0 - line.discount) / 100.0) - (purchase_price * line.product_uos_qty), 2)
        return res

    def __init__(self, registry, cr):
        """
            Overwriting _product_margin method and adding state "Suspended"
        """

        super(sale_order_line, self).__init__(registry, cr)

#        self._columns['margin']._fnct = self._product_margin

    _columns = {
        'price_unit': fields.float('Unit Price', help="Se abbonamento intero importo nell'anno ", required=True, digits_compute=dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'subscription': fields.related('product_id', 'subscription', type='boolean', string=_('Subscription')),
        'automatically_create_new_subscription': fields.boolean(_('Automatically create new subscription')),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Sale Price')),
        'suspended': fields.boolean(_('Suspended')),
        'partner_id': fields.related('order_id', 'partner_id', 'name', type='char', string=_('Customer'), store=True),
        'order_start_date': fields.related('order_id', 'order_start_date', type='date', string=_('Order Start')),
        'order_duration': fields.related('order_id', 'order_duration', type='selection', string=_('Duration'), selection=[
            (30, '1 month'),
            (60, '2 months'),
            (90, '3 months'),
            (120, '4 months'),
            (180, '6 months'),
            (365, '1 year'),
            (730, '2 years'),
            (1095, '3 years'),
        ]),
        'product_duration': fields.related('product_id', 'order_duration', type='selection', string=_('Duration'), selection=[
            (30, '1 month'),
            (60, '2 months'),
            (90, '3 months'),
            (120, '4 months'),
            (180, '6 months'),
            (365, '1 year'),
            (730, '2 years'),
            (1095, '3 years'),
        ]),
        'order_end_date': fields.related('order_id', 'order_end_date', type='date', string=_('Order End'), store=True),
        'user_id': fields.related('order_id', 'user_id', 'name', type='char', string=_('Salesman'), store=True),
        'section_id': fields.related('order_id', 'section_id', 'name', type='char', string=_('Sales Team'), store=True),
        'can_activate': fields.boolean("Activate ?")
    }

    _defaults = {
        'automatically_create_new_subscription': 0,
        'can_activate': 1,
        # 'suspended' : 1,
    }

    def amount_invoiced(self, cr, uid, order_line):
        """
            return: A total amount of invoices for these order line
        """
        partner_id = order_line.order_id.partner_id
        cr.execute(
            """SELECT SUM(account_invoice_line.price_subtotal)
            FROM account_invoice_line
            LEFT JOIN account_invoice
            ON account_invoice_line.invoice_id=account_invoice.id
            WHERE account_invoice_line.name=%s
            AND NOT account_invoice_line.invoice_id IS NULL
            AND account_invoice_line.origin_document=%s
            AND NOT account_invoice.state = 'cancel'
            AND account_invoice.partner_id = %s""", (order_line.name, 'sale.order.line, {}'.format(order_line.id), partner_id.id)
        )
        return cr.fetchall()[0][0]

    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):

        result = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product_id, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context)

        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context)
            result['value']['subscription'] = product.subscription
            if product.subscription:
                if product.order_duration:
                    ratio = 365 / product.order_duration
                else:
                    ratio = 1
                result['value'].update({
                    'price_unit': result['value']['price_unit'] * ratio
                })

        return result

    def action_suspend(self, cr, uid, line_ids, context):
        invoice_line_obj = self.pool['account.invoice.line']
        invoice_obj = self.pool['account.invoice']
        order_to_suspend = []
        all_invoices = []
        suspend_date = datetime.datetime.now()
        updated_invoice_ids = []
        for line in self.browse(cr, uid, line_ids, context=context):
            active_order_line_count = 0
            for oline in line.order_id.order_line:
                if not oline.suspended:
                    active_order_line_count += 1
            
            if active_order_line_count == 1:
                order_to_suspend.append(line.order_id.id)
            else:
                self.pool['sale.order.line'].write(cr, uid, line_ids, {'suspended': True}, context)
                invoice_lines = line.invoice_lines
                for invoice_line in invoice_lines:
                    invoice = invoice_line.invoice_id
                    invoice_date = datetime.datetime.strptime(
                        invoice.date_invoice,
                        DEFAULT_SERVER_DATE_FORMAT
                    )
                    if invoice.state == 'draft' and invoice_date.date() >= suspend_date.date():
                        updated_invoice_ids.append(invoice_line.invoice_id.id)
                        invoice_line_obj.unlink(cr, uid, invoice_line.id, context)
        # for invoice where a unlink line recalculate
        unlink_invoice_ids = []
        for invoice in invoice_obj.browse(cr, uid, updated_invoice_ids, context):
            if not invoice.invoice_line:
                unlink_invoice_ids.append(invoice.id)
            else:
                invoice.button_reset_taxes()

        if unlink_invoice_ids:
            invoice_obj.unlink(cr, uid, unlink_invoice_ids, context)

        if order_to_suspend:
            self.pool['sale.order'].suspend(cr, uid, order_to_suspend, context=context)

        #     invoice_line_ids = invoice_line_obj.search(cr, uid, [('origin_document', '=', 'sale.order.line, {}'.format(line_id))], context=context)
        #     if invoice_line_ids:
        #         for invoice_line in invoice_line_obj.browse(cr, uid, invoice_line_ids, context):
        #             if invoice_line.invoice_id.state == 'draft':
        #                 all_invoices.append(invoice_line.invoice_id)
        #                 invoice_line_obj.unlink(cr, uid, invoice_line.id, context)
        #
        # all_invoices = list(set(all_invoices))
        #
        # for invoice in all_invoices:
        #     if not invoice.invoice_line:
        #         self.pool['account.invoice'].unlink(cr, uid, invoice.id, context)

        return True

    def create_installment_invoice_line(self, cr, uid, order_line, invoice_period, invoice=False, context=None):
        sale_order_obj = self.pool['sale.order']
        sale_order_line_obj = self.pool['sale.order.line']

        # Calculate how much was invoiced
        invoiced = sale_order_line_obj.amount_invoiced(cr, uid, order_line) or 0
        remains_to_invoice = (order_line.price_unit * order_line.product_uom_qty) - invoiced
        if order_line.product_id.subscription:
            remains_to_invoice = order_line.price_unit * order_line.product_uom_qty / 12 * sale_order_obj.get_duration_in_months(order_line.order_id.order_duration) - invoiced

        # Control how much were invoiced and if 100% of line.price_unit is invoiced:
        if remains_to_invoice <= 0:
            _logger.debug(u'All invoices for line "%s: %s" order - %s are created' % (order_line.id, order_line.name, order_line.order_id.name))

            sale_order_line_obj.write(cr, uid, [order_line.id], {'invoiced': True}, context)
            invoice_line_ids = False
        else:
            # Make an invoice and add a new line in account.invoice
            _logger.debug(u'Adding new invoice line for line "%s: %s" (order - %s)' % (order_line.id, order_line.name, order_line.order_id.name))

            # Create account.invoice.line:
            # This function writes total price and not just installment
            # It also set 'invoiced' to True
            invoice_line_ids = sale_order_line_obj.invoice_line_create(cr, uid, [order_line.id], context)

            # Adjust price_unit of invoice.line
            sale_order_obj.adjust_price(cr, uid, order_line, invoice_line_ids, remains_to_invoice, invoice_period)
            values = {'origin_document': 'sale.order.line, {0}'.format(str(order_line.id))}
            if invoice:
                values.update({
                    'invoice_id': invoice.id,
                    'company_id': invoice.company_id.id,
                    'partner_id': invoice.partner_id.id
                })
            self.pool['account.invoice.line'].write(cr, uid, invoice_line_ids, values, context)

        return invoice_line_ids

    def action_restore(self, cr, uid, line_ids, context):
        self.pool['sale.order.line'].write(cr, uid, line_ids, {
            'suspended': False,
            'invoiced': False
        }, context)
        invoice_obj = self.pool['account.invoice']
        sale_order_obj = self.pool['sale.order']
        sale_order_line_obj = self.pool['sale.order.line']
        
        for order_line in self.browse(cr, uid, line_ids, context):
            if order_line.order_id.state == "suspended":
                self.pool['sale.order'].write(cr, uid, [order_line.order_id.id], {'state': 'progress'}, context)
                sale_order_obj.auto_invoice(cr, uid, order_line.order_id.id, context)
                continue
            invoice_ids = invoice_obj.search(cr, uid, [('origin', '=', order_line.order_id.name), ('state', '=', 'draft')], context=context)
            invoice_dates = sale_order_obj.get_invoice_dates(cr, uid, order_line.order_id, order_line.order_id.order_duration, order_line.order_id.order_invoice_duration, context=context)
            invoice_date_period = {invoice_data['invoice_date']: invoice_data['period'] for invoice_data in invoice_dates}

            if invoice_ids:
                for invoice in invoice_obj.browse(cr, uid, invoice_ids, context):
                    # add/create line with correct amount
                    invoice_period = invoice_date_period.get(invoice.date_invoice, False)
                    if invoice_period:
                        sale_order_line_obj.create_installment_invoice_line(cr, uid, order_line, invoice_period, invoice)
                    else:
                        _logger.error(_('Calculated invoice date differ from real date ({})').format(invoice.date_invoice))
            else:
                sale_order_obj.auto_invoice(cr, uid, order_line.order_id.id, context)
        return True

    def create(self, cr, uid, values, context=None):
        if values.get('product_id') and values.get('order_id'):
            product = self.pool['product.product'].browse(cr, uid, values['product_id'], context)
            order = self.pool['sale.order'].browse(cr, uid, values['order_id'], context)
            if product.subscription and not order.have_subscription:
                raise orm.except_orm(_('Error'), _("You've added subscriptable product to an order which has no Payments in Installments"))
        return super(sale_order_line, self).create(cr, uid, values, context)

    def write(self, cr, uid, ids, values, context=None):
        if values.get('product_id'):
            product = self.pool['product.product'].browse(cr, uid, values['product_id'], context)
            for order_line in self.browse(cr, uid, ids, context):
                if product.subscription and not order_line.order_id.have_subscription:
                    raise orm.except_orm(_('Error'), _("You've added subscriptable product to an order which has no Payments in Installments"))
        return super(sale_order_line, self).write(cr, uid, ids, values, context)

    def action_dummy(self, cr, uid, line_ids, context):
        return True

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        # no reason to sum price_units
        fields.remove('price_unit')
        result = super(sale_order_line, self).read_group(cr, uid, domain, fields, groupby, offset, limit=limit, context=context, orderby=orderby)

        if groupby:
            group_key = groupby[0]
            cr.execute("""SELECT {g_key}, SUM(price_unit * product_uom_qty) AS subtotal
                FROM sale_order_line
                WHERE state NOT IN ('draft')
                AND suspended = 'false'
                GROUP BY {g_key}
            """.format(g_key=group_key))

            partners_subtotal = {row[group_key]: row['subtotal'] for row in cr.dictfetchall()}

            for row in result:
                if isinstance(row[group_key], (list, tuple)):
                    g_key = row[group_key][0]
                else:
                    g_key = row[group_key]
                row['price_subtotal'] = partners_subtotal.get(g_key, 0)

        return result


class sale_order(orm.Model):
    _inherit = "sale.order"
    _logger = netsvc.Logger()

    def __init__(self, registry, cr):
        """
            Add state "Suspended"
        """

        super(sale_order, self).__init__(registry, cr)
        option = ('suspended', 'Suspended')

        type_selection = self._columns['state'].selection
        if option not in type_selection:
            type_selection.append(option)

    def get_order_end_date(self, cr, uid, ids, field_name, arg, context=None):
        value = {}
        
        for order in self.browse(cr, uid, ids, context):
            if field_name == 'order_end_date' and not order.have_subscription:
                value[order.id] = False
            else:
                if order.order_start_date:
                    start_date = datetime.datetime.strptime(order.order_start_date, DEFAULT_SERVER_DATE_FORMAT)
                else:
                    start_date = datetime.datetime.now()
                
                if order.order_duration:
                    end_date = start_date + relativedelta(months=self.get_duration_in_months(order.order_duration)) - datetime.timedelta(days=1)
                else:
                    end_date = start_date + relativedelta(months=self.get_duration_in_months(365)) - datetime.timedelta(days=1)
                value[order.id] = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        
        return value
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool['sale.order.line'].browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        orders = self.browse(cr, uid, ids, context)
        for order in orders:
            if order.origin and order.state in ('draft',):
                value[order.id] = 'orange'
                continue
            elif order.state == 'cancel':
                value[order.id] = 'grey'
            elif order.state in ('wait_ship', 'wait_invoice', 'manual'):
                value[order.id] = 'green'
            elif order.state in ('wait_valid',):
                value[order.id] = 'red'
            elif order.state in ('wait_correct',):
                value[order.id] = 'fuchsia'
            elif order.state in ('invoice_except', 'shipping_except'):
                value[order.id] = 'blue'
            else:
                value[order.id] = 'black'

        return value
        
    _columns = {
        'presentation': fields.boolean('Allega Presentazione'),
        'automatically_create_new_subscription': fields.boolean('Automatically create new subscription', readonly=False, required=False, 
                                                                states={
                                                                    'progress': [('readonly', False)],
                                                                    'done': [('readonly', True)],
                                                                    'cancel': [('readonly', True)]
                                                                }),
        'have_subscription': fields.boolean('Payment in installments', readonly=False,
                                            states={
                                                'progress': [('readonly', True)],
                                                'done': [('readonly', True)],
                                                'cancel': [('readonly', True)]
                                            }, help="If set, the total sale price will be allocated in the number of invoices provided by the order in which you enter the product" ),
        'order_duration': fields.selection(
            [
                (30, '1 month'),
                (60, '2 months'),
                (90, '3 months'),
                (120, '4 months'),
                (180, '6 months'),
                (365, '1 year'),
                (730, '2 years'),
                (1095, '3 years'),
            ],
            'Subscription Duration',
            help='Subscription duration in days',
            states={
                'progress': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]
            },
            readonly=False),
        'order_invoice_duration': fields.selection(
            [
                (30, 'Monthly'),
                (60, 'Bimestral'),
                (90, 'Trimestral'),
                (180, 'Semiannual'),
                (365, 'Annual'),
                (730, 'Biennial'),
                (1095, 'Triennial'),
            ], 'Invoice Period',
            help='Invoice Period',
            states={
                'progress': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]
            },
            readonly=False),
        'order_start_date': fields.date('Subscription Beginning Date', readonly=False, required=False, 
                                        states={
                                            'progress': [('readonly', True)],
                                            'done': [('readonly', True)],
                                            'cancel': [('readonly', True)]
                                        }),
        'order_end_date': fields.function(get_order_end_date, 'Subscription Ending Date', type='date', readonly=True, method=True),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,),
        'subscription_invoice_day': fields.selection((
            ('1', _('First day of month')),
            ('31', _('Last day of month'))
        ), _('Invoice Day')),
    }

    _defaults = {
        'subscription_invoice_day': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.subscription_invoice_day,
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        if not default:
            default = {}

        # We want supplier_invoice_number, cig, cup to be recreated:
        default.update({
            'order_start_date': False,
        })
        return super(sale_order, self).copy(cr, uid, ids, default, context)

    def _amount_line_tax(self, cr, uid, line, context=None):
        if line.order_id.have_subscription and line.subscription:
            val = 0.0

            # for c in self.pool['account.tax'].compute_all(cr, uid, line.tax_id, line.price_subtotal * (1 - (line.discount or 0.0) / 100.0), line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
            for c in self.pool['account.tax'].compute_all(cr, uid, line.tax_id, line.price_unit * (1 - (line.discount or 0.0) / 100.0), line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
                val += c.get('amount', 0.0)
            return val
        else:
            return super(sale_order, self)._amount_line_tax(cr, uid, line, context)

    def renew_orders(self, cr, uid, anticipation, context=None):
        """
            This function is called by cron.
            It automatically creates new order and corresponding order lines
        """

        if context and 'anticipation' in context:
            cron_ids = self.pool['ir.cron'].search(cr, uid, [('function', '=', 'renew_orders')], context=context)
            if cron_ids:
                cron = self.pool['ir.cron'].browse(cr, uid, cron_ids[0], context)
                anticipate = datetime.timedelta(days=int(cron.args.strip("(',)")))
            else:
                anticipate = datetime.timedelta(days=0)
        elif anticipation.isdigit():
            anticipate = datetime.timedelta(days=int(anticipation))
        else:
            anticipate = datetime.timedelta(days=0)
        
        line_obj = self.pool['sale.order.line']
        order_obj = self.pool['sale.order']
        
        two_years_ago = datetime.datetime.now() - relativedelta(years=3)
        
        # Find all orders that should be renewed:
        # order_ids = order_obj.search(cr, uid, [('automatically_create_new_subscription', '=', True), ('order_start_date', '>', two_years_ago), ('state', 'not in', ('draft', 'cancel', 'wait_valid'))])
        order_ids = order_obj.search(cr, uid, [('automatically_create_new_subscription', '=', True), ('order_start_date', '>', two_years_ago), ('state', 'in', ('progress',))], context=context)
        
        order_end_dates = self.get_order_end_date(cr, uid, order_ids, '', '')

        for order_id in order_ids:
            order_end_date = datetime.datetime.strptime(order_end_dates[order_id], DEFAULT_SERVER_DATE_FORMAT)

            if order_end_date - anticipate < datetime.datetime.now():
                order = order_obj.browse(cr, uid, order_id, context)
                _logger.debug(u"Renewing order %s.\nOrder started %s, lasts for %s days and finished %s" % (order.name, order.order_start_date, order.order_duration, order_end_date))
                values = {
                    'order_start_date': order_end_date + datetime.timedelta(days=1),
                    'validation_date': False,
                    'origin': order.name,
                    'validation_user': False
                }
                new_order_id = self.copy(cr, uid, order.id, values)
                
                order_obj.write(cr, uid, [order.id], {'automatically_create_new_subscription': False}, context)
                
                new_line_ids = line_obj.search(cr, uid, [('order_id', '=', new_order_id)], context=context)
                new_lines = line_obj.browse(cr, uid, new_line_ids, context)
                for line in new_lines:
                    if not line.product_id.subscription or line.suspended:
                        line_obj.unlink(cr, uid, [line.id])
        
        # We should return smth, if not we will get an error
        return {'value': {}}
    
    # def copy(self, cr, uid, id, values=None, context=None):
    #    new_order_id = super(sale_order, self).copy(cr, uid, id)
    #    self.write(cr, uid, [new_order_id], values)
    #    return new_order_id

    # def new_order(self, cr, uid, line_id, context=None):
    #     """
    #         We should keep this function for a compatibility with old procedure.
    #         Evaluate if this function can be deleted after november 2014.
    #     """
    #     return True

    def action_wait(self, cr, uid, ids, *args):
        """
            Function is called when Order is Confirmed
        """

        for order in self.browse(cr, uid, ids):
            values = {
                'date_confirm': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            }
            if order.order_policy == 'manual' or order.have_subscription:
                if not order.order_policy == 'manual':
                    values['order_policy'] = 'manual'
                values['state'] = 'manual'
                self.write(cr, uid, [order.id], values)
            else:
                values['state'] = 'progress'
                self.write(cr, uid, [order.id], values)
                
            self.pool['sale.order.line'].button_confirm(cr, uid, [line.id for line in order.order_line])
            message = _("The quotation '%s' has been converted to a sales order.") % (order.name,)
            self.log(cr, uid, order.id, message)
                
        return True

    def manual_invoice(self, cr, uid, ids, context=None):
        if len(ids) == 1:
            order = self.browse(cr, uid, ids[0], context)
            if order.have_subscription:
                values = {
                    'state': 'progress',
                    'date_confirm': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                }
                if not order.order_start_date:
                    values['order_start_date'] = datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
                self.write(cr, uid, [order.id], values)
                self.auto_invoice(cr, uid, ids, context=None)
                return True

        return super(sale_order, self).manual_invoice(cr, uid, ids, context)

    @staticmethod
    def get_duration_in_months(duration_in_days):
        duration = {
            1095: 36,
            730: 24,
            365: 12,
            180: 6,
            90: 3,
            60: 2,
            30: 1,
        }
        return duration[duration_in_days]

    def adjust_price(self, cr, uid, order_line, invoice_line_ids, remains_to_invoice, period):
        if not order_line.product_id.subscription:
            return
        
        duration = self.get_duration_in_months(order_line.order_id.order_duration)
        invoice_duration = self.get_duration_in_months(order_line.order_id.order_invoice_duration)
        payments_quantity = duration / invoice_duration
        if payments_quantity <= 0:
            raise orm.except_orm(_('Error'), _("You've configured Subscription duration with less period of Invoicing Period."))
        
        invoice_line = self.pool['account.invoice.line'].browse(cr, uid, invoice_line_ids[0])

        price_unit = invoice_line.price_unit
        # price is for annual usage of a product
        price_unit = round(price_unit / 12 * duration / payments_quantity,
                           self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price'))
        
        if remains_to_invoice - price_unit * invoice_line.quantity < price_unit * invoice_line.quantity / 2:
            price_unit = remains_to_invoice / invoice_line.quantity
            invoiced = True
        else:
            invoiced = False
        
        ## Adjust price_unit
        self.pool['account.invoice.line'].write(cr, uid, [invoice_line.id], {'price_unit': price_unit, 'note': period})
            
        self.pool['sale.order.line'].write(cr, uid, [order_line.id], {'invoiced': invoiced})

    def get_invoice_dates(self, cr, uid, order, order_duration, order_invoice_duration, delta_month=0, context={}):
        """
        Period is always for time after invoice
        :param cr:
        :param uid:
        :param order:
        :param order_duration:
        :param order_invoice_duration:
        :param context:
        :return: list of dictionaries containing invoice_date and period of time for which this invoice is applied
        """
        # order = self.browse(cr, uid, order_id, context)
        # user = self.pool['res.users'].browse(cr, uid, uid, context)
        if order.order_start_date:
            start_date = datetime.datetime.strptime(order.order_start_date, DEFAULT_SERVER_DATE_FORMAT)
        else:
            start_date = datetime.date.today()

        day_delta = datetime.timedelta(1)
        
        order_duration = self.get_duration_in_months(order_duration)
        invoice_duration = self.get_duration_in_months(order_invoice_duration)
        payments_quantity = order_duration / invoice_duration
        
        invoice_delta = relativedelta(months=self.get_duration_in_months(order_invoice_duration))

        virtual_start_date = datetime.datetime(start_date.year, start_date.month, 1)
        if order.subscription_invoice_day == '31':
            virtual_start_date += relativedelta(months=1)

        invoice_date = start_date
        if delta_month:
            invoice_date += relativedelta(months=delta_month)

        if invoice_duration == 1:
            dates = [{'invoice_date': invoice_date.strftime(DEFAULT_SERVER_DATE_FORMAT), 'period': virtual_start_date.strftime('%B %Y')}]
        else:
            period_end = virtual_start_date + invoice_delta - relativedelta(months=1)
            dates = [{'invoice_date': invoice_date.strftime(DEFAULT_SERVER_DATE_FORMAT), 'period': virtual_start_date.strftime('%B %Y') + ' - ' + period_end.strftime('%B %Y')}]

        datetime_date = virtual_start_date

        for k in range(1, payments_quantity):
            datetime_date += invoice_delta

            invoice_date = datetime_date
            period_end = invoice_date + invoice_delta - day_delta

            if delta_month:
                invoice_date += relativedelta(months=delta_month)

            if order.subscription_invoice_day == '31':
                invoice_date = invoice_date - day_delta
            
            if invoice_duration == 1:
                dates.append({'invoice_date': invoice_date.strftime(DEFAULT_SERVER_DATE_FORMAT), 'period': datetime_date.strftime('%B %Y')})
            else:
                dates.append({'invoice_date': invoice_date.strftime(DEFAULT_SERVER_DATE_FORMAT), 'period': datetime_date.strftime('%B %Y') + ' - ' + period_end.strftime('%B %Y')})
        return dates

    def auto_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        if not ids:
            return False
        elif not isinstance(ids, (list, tuple)):
            ids = [ids]

        _logger.debug(u'Creating invoices...')

        def make_invoice(order, lines, invoice_values):
            """
                 To make invoices.

                 @param order:
                 @param lines:

                 @return:
            """
            
            a = order.partner_id.property_account_receivable.id
            if order.partner_id and order.partner_id.property_payment_term.id:
                pay_term = order.partner_id.property_payment_term.id
            else:
                pay_term = False

            inv = {
                'name': order.name,
                'origin': order.name,
                'date_invoice': invoice_values['invoice_date'],
                'type': 'out_invoice',
                'reference': "P%dSO%d" % (order.partner_id.id, order.id),
                'account_id': a,
                'partner_id': order.partner_id.id,
                'address_invoice_id': order.partner_invoice_id.id,
                'address_contact_id': order.partner_invoice_id.id,
                'invoice_line': [(6, 0, lines)],
                'currency_id': order.pricelist_id.currency_id.id,
                'comment': order.note,
                'payment_term': pay_term,
                'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            }
            
            inv_id = self.pool['account.invoice'].create(cr, uid, inv, context)
            return inv_id

        order_id = ids[0]
        order = self.browse(cr, uid, order_id, context)
        sale_order_line_obj = self.pool['sale.order.line']
        account_invoice_obj = self.pool['account.invoice']

        # Find all active sale.order.line (invoiced == False)
        domain = [
            ('invoiced', '=', False),
            ('state', '!=', 'cancel'),
            ('order_id', '=', order_id),
            ('suspended', '=', False)
        ]

        sale_order_line_ids = sale_order_line_obj.search(cr, uid, domain, context=context)
        invoice_dates = self.get_invoice_dates(cr, uid, order, order.order_duration, order.order_invoice_duration, context=context)
        activation_date = datetime.datetime.now()
        # Check if there are already invoices for this order
        active_invoice_ids = account_invoice_obj.search(cr, uid, [
            ('origin', '=', order.name),
            ('state', 'not in', ['cancel'])
            # ('date_invoice', '>', activation_date.strftime(DEFAULT_SERVER_DATE_FORMAT ))
        ])
        if active_invoice_ids:
            active_invoice_dates = [invoice.date_invoice for invoice in account_invoice_obj.browse(cr, uid, active_invoice_ids, context)]
        else:
            active_invoice_dates = []

        for invoice_date in invoice_dates:
            
            if invoice_date['invoice_date'] in active_invoice_dates:
                continue

            new_invoice_line_ids = []
            # For every not invoiced line in active order:        
            for order_line in sale_order_line_obj.browse(cr, uid, sale_order_line_ids, context):
                invoice_line_ids = sale_order_line_obj.create_installment_invoice_line(cr, uid, order_line, invoice_date['period'], context=context)
                if invoice_line_ids:
                    new_invoice_line_ids += invoice_line_ids

            if new_invoice_line_ids:
                invoice_id = make_invoice(order, new_invoice_line_ids, invoice_date)
                cr.execute("""INSERT INTO sale_order_invoice_rel
                           (order_id, invoice_id) values (%s, %s)""", (order_id, invoice_id))

    def suspend(self, cr, uid, ids, context):
        wf_service = netsvc.LocalService('workflow')
        account_invoice_obj = self.pool['account.invoice']
        sale_order_line_obj = self.pool['sale.order.line']

        for order in self.browse(cr, uid, ids, context):
            _logger.debug(u'Suspending order {0}'.format(order.name))
            if order.have_subscription:
                invoices2cancel = account_invoice_obj.search(
                    cr, uid,
                    [
                     ('origin', '=', order.name),
                     ('date_invoice', '>=', datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))]
                )
                for invoice in account_invoice_obj.browse(cr, uid, invoices2cancel, context):
                    if invoice.state == 'draft':
                        print "canceling invoice {0} ({1})...".format(invoice.name, invoice.id)
                        wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_cancel', cr)
                        account_invoice_obj.unlink(cr, uid, invoice.id, context)

                for line in order.order_line:
                    if line.product_id.subscription:
                        update_line_vals = {
                            'suspended': True,
                        }
                        invoiced = sale_order_line_obj.amount_invoiced(cr, uid, line) or 0
                        if invoiced < line.price_subtotal:
                            update_line_vals.update({'invoiced': False})
                        sale_order_line_obj.write(cr, uid, line.id, update_line_vals, context)

        self.write(cr, uid, ids, {'state': 'suspended'})
        return True

    def reactivate(self, cr, uid, ids, context):
        print "Reactivating..."

        for order in self.browse(cr, uid, ids, context):
            _logger.debug(u'Reactivating order {0}'.format(order.name))
            line_ids = [line.id for line in order.order_line]
            self.pool.get('sale.order.line').write(cr, uid, line_ids, {'suspended': False}, context=context)
            self.auto_invoice(cr, uid, order.id, context=None)

        self.write(cr, uid, ids, {'state': 'progress'})

        return True

    def close(self, cr, uid, ids, context):
        """
        The button "Close" is visible only if order is already suspended. It will
        cancel order if there are no invoices or set 'done' if there are already any
        """

        wf_service = netsvc.LocalService('workflow')
        sale_order_line_obj = self.pool['sale.order.line']
        invoiced = 0
        for order in self.browse(cr, uid, ids, context):
            _logger.debug(u'Closing order {0}'.format(order.name))
            for line in order.order_line:
                if line.product_id.subscription:
                    invoiced += sale_order_line_obj.amount_invoiced(cr, uid, line) or 0

            if invoiced:
                if not order.shipped:
                    self.pool['procurement.order'].run_scheduler(cr, uid, automatic=False, use_new_cursor=False, context=context)

                self.write(cr, uid, order.id, {'state': 'progress'})
                wf_service.trg_validate(uid, 'sale.order', order.id, 'all_lines', cr)
            else:
                wf_service.trg_validate(uid, 'sale.order', order.id, 'cancel', cr)
        return True
