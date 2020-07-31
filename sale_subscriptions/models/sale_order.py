# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012-2017 Didotech (<http://www.didotech.com>).
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

import datetime
import logging
import time

import netsvc
from dateutil.relativedelta import relativedelta
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

# locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


ORDER_DURATION = [
            (30, '1 month'),
            (60, '2 months'),
            (90, '3 months'),
            (120, '4 months'),
            (180, '6 months'),
            (365, '1 year'),
            (730, '2 years'),
            (1095, '3 years'),
            (1460, '4 years'),
            (1825, '5 years')
        ]


class SaleOrder(orm.Model):
    _inherit = "sale.order"
    _logger = netsvc.Logger()

    def __init__(self, registry, cr):
        """
            Add state "Suspended"
        """

        super(SaleOrder, self).__init__(registry, cr)
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
        'automatically_create_new_subscription': fields.boolean('Automatically create new subscription', readonly=False,
                                                                required=False,
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
                                            },
                                            help="If set, the total sale price will be allocated in the number of invoices provided by the order in which you enter the product"),
        'order_duration': fields.selection(ORDER_DURATION, 'Subscription Duration',
                                           help='Subscription duration in days',
                                           states={
                                               'progress': [('readonly', True)],
                                               'done': [('readonly', True)],
                                               'cancel': [('readonly', True)]
                                           },
                                           readonly=False),
        'order_invoice_duration': fields.selection(ORDER_DURATION, 'Invoice Period',
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
        'order_end_date': fields.function(get_order_end_date, 'Subscription Ending Date', type='date', readonly=True,
                                          method=True),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True, ),
        'subscription_invoice_day': fields.selection((
            ('1', _('First day of month')),
            ('31', _('Last day of month'))
        ), _('Invoice Day')),
    }

    _defaults = {
        'subscription_invoice_day': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.subscription_invoice_day,
        'order_duration': 30,
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
        return super(SaleOrder, self).copy(cr, uid, ids, default, context)

    def _amount_line_tax(self, cr, uid, line, context=None):
        if line.order_id.have_subscription and line.subscription:
            val = 0.0

            # for c in self.pool['account.tax'].compute_all(cr, uid, line.tax_id, line.price_subtotal * (1 - (line.discount or 0.0) / 100.0), line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
            for c in self.pool['account.tax'].compute_all(cr, uid, line.tax_id, line.price_unit * (1 - (line.discount or 0.0) / 100.0), line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
                val += c.get('amount', 0.0)
            return val
        else:
            return super(SaleOrder, self)._amount_line_tax(cr, uid, line, context)

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
                new_order_id = self.copy(cr, uid, [order.id], values, context)
                
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
        res = super(SaleOrder, self).action_wait(cr, uid, ids, *args)
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
                
        return res

    def manual_invoice(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if len(ids) == 1:
            order = self.browse(cr, uid, ids[0], context)
            if order.have_subscription:
                values = {
                    'state': 'progress',
                    'date_confirm': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                }
                if not order.order_start_date:
                    values['order_start_date'] = datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
                self.write(cr, uid, [order.id], values, context)
                self.auto_invoice(cr, uid, ids, context)
                return True

        return super(SaleOrder, self).manual_invoice(cr, uid, ids, context)

    @staticmethod
    def get_duration_in_months(duration_in_days):
        duration = {
            1825: 60,
            1460: 48,
            1095: 36,
            730: 24,
            547: 18,
            365: 12,
            180: 6,
            120: 4,
            90: 3,
            60: 2,
            30: 1
        }
        return duration[duration_in_days]

    def adjust_price(self, cr, uid, order_line, invoice_line_ids, remains_to_invoice, period, context=None):
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
        
        if abs(remains_to_invoice - price_unit * invoice_line.quantity) < abs(price_unit * invoice_line.quantity / 2):
            price_unit = remains_to_invoice / invoice_line.quantity
            invoiced = True
        else:
            invoiced = False
        
        ## Adjust price_unit
        self.pool['account.invoice.line'].write(cr, uid, [invoice_line.id], {'price_unit': price_unit, 'note': period}, context)
        if not invoiced:
            order_line.write({'invoiced': invoiced})
        return True

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
        context = context or self.pool['res.users'].context_get(cr, uid)

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
            pay_term = order.payment_term and order.payment_term.id or order.partner_id and order.partner_id.property_payment_term.id or False

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
        return True

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
                        print("canceling invoice {0} ({1})...".format(invoice.name, invoice.id))
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

    def button_dummy(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(SaleOrder, self).button_dummy(cr, uid, ids, context)
        order_line_obj = self.pool['sale.order.line']
        order_line_ids = order_line_obj.search(cr, uid, [('order_id', 'in', ids)], context=context)
        order_line_obj.write(cr, uid, order_line_ids, {}, context=context)
        self.write(cr, uid, ids, {}, context=context)
        return res
