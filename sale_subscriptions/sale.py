# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012-2014 Didotech (<http://www.didotech.com>).
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

LOGGER = netsvc.Logger()

import locale
locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
#locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool['account.tax']
        cur_obj = self.pool['res.currency']
        order_obj = self.pool['sale.order']
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            if line.order_id.have_subscription and line.product_id.subscription:
                k = order_obj.getDurationInMonths(line.order_id.order_duration) / 12.0
                res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'] * k)
            else:
                res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    #def _amount_line(self, cr, uid, ids, field_name, order_duration, context=None):
    #    tax_obj = self.pool.get('account.tax')
    #    cur_obj = self.pool.get('res.currency')
    #    order_obj = self.pool.get('sale.order')
    #    res = {}
    #    if context is None:
    #        context = {}
    #    for line in self.browse(cr, uid, ids, context=context):
    #        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #        taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
    #        cur = line.order_id.pricelist_id.currency_id
    #        if line.order_id.have_subscription or order_duration and line.product_id.subscription:
    #            if order_duration:
    #                k = order_obj.getDurationInMonths(order_duration) / 12.0
    #            else:
    #                k = order_obj.getDurationInMonths(line.order_id.order_duration) / 12.0
    #            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'] * k)
    #        else:
    #            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
    #    return res

    _columns = {
        'price_unit': fields.float('Unit Price', help="Se abbonamento intero importo nell'anno ", required=True, digits_compute= dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'subscription': fields.related('product_id', 'subscription', type='boolean', string='Subscription'),
        'automatically_create_new_subscription': fields.boolean('Automatically create new subscription'),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute=dp.get_precision('Sale Price')),
    }

    _defaults = {
        'automatically_create_new_subscription': 0,
    }

    def amount_invoiced(self, cr, uid, line):
        """
            return: A total amount of invoices for these order line
        """

        cr.execute(
            """SELECT SUM(account_invoice_line.price_subtotal)
            FROM account_invoice_line LEFT JOIN account_invoice
            ON account_invoice_line.invoice_id=account_invoice.id
            WHERE account_invoice_line.name=%s
            AND NOT account_invoice_line.invoice_id IS NULL
            AND account_invoice_line.origin=%s
            AND NOT account_invoice.state = 'cancel'""", (line.name, line.order_id.name)
        )
        return cr.fetchall()[0][0]


class sale_order(orm.Model):
    _inherit = "sale.order"
    _logger = netsvc.Logger()

    # def __init__(self, cr, uid, context=None):
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
        # TODO: rewrite to use relativedelta
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
                    end_date = start_date + relativedelta(months=self.getDurationInMonths(order.order_duration)) - datetime.timedelta(days=1)
                else:
                    end_date = start_date + relativedelta(months=self.getDurationInMonths(365)) - datetime.timedelta(days=1)
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
                (180, '6 months'),
                (365, '1 year'),
                (730, '2 years')
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
                (730, 'Biennial')
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
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,)
    }

    def renew_orders(self, cr, uid, anticipation, context=None):
        """
            This function is called by cron.
            It automatically creates new order and corresponding order lines
        """

        if context and 'anticipation' in context:
            cron_ids = self.pool['ir.cron'].search(cr, uid, [('function', '=', 'renew_orders')])
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
        
        two_years_ago = datetime.datetime.now() - relativedelta(years=2)
        
        # Find all orders that should be renewed:
        #order_ids = order_obj.search(cr, uid, [('automatically_create_new_subscription', '=', True), ('order_start_date', '>', two_years_ago), ('state', 'not in', ('draft', 'cancel', 'wait_valid'))])
        order_ids = order_obj.search(cr, uid, [('automatically_create_new_subscription', '=', True), ('order_start_date', '>', two_years_ago), ('state', 'in', ('progress',))])
        
        order_end_dates = self.get_order_end_date(cr, uid, order_ids, '', '')

        for order_id in order_ids:
            order_end_date = datetime.datetime.strptime(order_end_dates[order_id], DEFAULT_SERVER_DATE_FORMAT)

            if order_end_date - anticipate < datetime.datetime.now():
                order = order_obj.browse(cr, uid, order_id, context)
                LOGGER.notifyChannel(self._name, netsvc.LOG_DEBUG, "Renewing order %s.\nOrder started %s, lasts for %s days and finished %s" % (order.name, order.order_start_date, order.order_duration, order_end_date))
                values = {
                    'order_start_date': order_end_date + datetime.timedelta(days=1),
                    'validation_date': False,
                    'origin': order.name,
                    'validation_user': False
                }
                new_order_id = self.copy(cr, uid, order.id, values)
                
                order_obj.write(cr, uid, [order.id], {'automatically_create_new_subscription': False})
                
                new_line_ids = line_obj.search(cr, uid, [('order_id', '=', new_order_id)])
                new_lines = line_obj.browse(cr, uid, new_line_ids, context)
                for line in new_lines:
                    if not line.product_id.subscription:
                        line_obj.unlink(cr, uid, [line.id])
        
        # We should return smth, if not we will get an error
        return {'value': {}}
    
    #def copy(self, cr, uid, id, values=None, context=None):
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
    
    def getDurationInMonths(self, duration_in_days):
        duration = {
            730: 24,
            365: 12,
            180: 6,
            90: 3,
            60: 2,
            30: 1,
        }
        return duration[duration_in_days]

    def adjustPrice(self, cr, uid, sale_order_line, invoice_line_ids, remains_to_invoice, period):
        if not sale_order_line.product_id.subscription:
            return
        
        duration = self.getDurationInMonths(sale_order_line.order_id.order_duration)
        invoice_duration = self.getDurationInMonths(sale_order_line.order_id.order_invoice_duration)
        payments_quantity = duration / invoice_duration
        
        invoice_line = self.pool['account.invoice.line'].browse(cr, uid, invoice_line_ids[0])

        price_unit = invoice_line.price_unit
        
        # Il price is for annual usage of a product
        price_unit = round(price_unit / 12 * duration / payments_quantity,
                            self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price'))
        
        if remains_to_invoice - price_unit * invoice_line.quantity < price_unit * invoice_line.quantity / 2:
            price_unit = remains_to_invoice / invoice_line.quantity
            invoiced = True
        else:
            invoiced = False
        
        ## Adjust price_unit
        self.pool['account.invoice.line'].write(cr, uid, [invoice_line.id], {'price_unit': price_unit, 'note': period})
            
        if invoiced:
            self.pool['sale.order.line'].write(cr, uid, [sale_order_line.id], {'invoiced': True})
        else:
            self.pool['sale.order.line'].write(cr, uid, [sale_order_line.id], {'invoiced': False})

    def getInvoiceDates(self, cr, uid, order_id, context):
        order = self.browse(cr, uid, order_id, context)
        invoicing_date = []
        start_date = datetime.datetime.strptime(order.order_start_date, DEFAULT_SERVER_DATE_FORMAT)
        #start_date += relativedelta(months=1)

        virtual_start_date_str = '%s-%s-%s' % (start_date.year, start_date.month, '1')
        virtual_start_date = datetime.datetime.strptime(virtual_start_date_str, DEFAULT_SERVER_DATE_FORMAT)
        
        day_delta = datetime.timedelta(1)
        
        order_duration = self.getDurationInMonths(order.order_duration)
        invoice_duration = self.getDurationInMonths(order.order_invoice_duration)
        payments_quantity = order_duration / invoice_duration
        
        invoice_delta = relativedelta(months=self.getDurationInMonths(order.order_invoice_duration))
        
        datetime_date = virtual_start_date
        
        if invoice_duration == 1:
            dates = [{'invoice_date': order.order_start_date, 'period': start_date.strftime('%B %Y')},]
        else:
            period_end = start_date + invoice_delta - relativedelta(months=1)
            dates = [{'invoice_date': order.order_start_date, 'period': start_date.strftime('%B %Y') + ' - ' + period_end.strftime('%B %Y')},]
        
        for k in range(1, payments_quantity):
            datetime_date += invoice_delta
            ## Invoicing on the last day of month:
            #invoice_date = datetime_date - day_delta
            #period_end = invoice_date + invoice_delta
            
            ## Invoicing on the first day of next month:
            invoice_date = datetime_date
            period_end = invoice_date + invoice_delta - day_delta
            
            if invoice_duration == 1:
                dates.append({'invoice_date': invoice_date.strftime(DEFAULT_SERVER_DATE_FORMAT), 'period': datetime_date.strftime('%B %Y')})
            else:
                dates.append({'invoice_date': invoice_date.strftime(DEFAULT_SERVER_DATE_FORMAT), 'period': datetime_date.strftime('%B %Y') + ' - ' + period_end.strftime('%B %Y')})
    
        return dates
    
    # def amount_invoiced(self, cr, uid, line):
    #     """
    #         return: A total amount of invoices for these order line
    #     """
    #
    #     cr.execute("SELECT SUM(price_subtotal) FROM account_invoice_line WHERE name=%s AND NOT invoice_id IS NULL AND origin=%s", (line.name, line.order_id.name))
    #     return cr.fetchall()[0][0]
        
    def auto_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        if not ids:
            return False
        elif not isinstance(ids, (list, tuple)):
            ids = [ids]

        # wf_service = netsvc.LocalService('workflow')
        
        LOGGER.notifyChannel(self._name, netsvc.LOG_DEBUG, 'Creating invoices...')
        
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
                'currency_id' : order.pricelist_id.currency_id.id,
                'comment': order.note,
                'payment_term': pay_term,
                'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            }
            
            inv_id = self.pool['account.invoice'].create(cr, uid, inv)
            return inv_id

        order_id = ids[0]
        sale_order_line_obj = self.pool['sale.order.line']

        # Find all active sale.order.line (invoiced == False)
        sale_order_line_ids = sale_order_line_obj.search(cr, uid, [('invoiced', '=', False), ('state', '!=', 'cancel'), ('order_id', '=', order_id)])

        invoice_dates = self.getInvoiceDates(cr, uid, order_id, context)
        for invoice_date in invoice_dates:
            invoices = {}
            # For every not invoiced line in active order:        
            for line in sale_order_line_obj.browse(cr, uid, sale_order_line_ids, context):
                # Calculate how much was invoiced
                invoiced = sale_order_line_obj.amount_invoiced(cr, uid, line) or 0
                remains_to_invoice = line.price_unit * line.product_uom_qty / 12 * self.getDurationInMonths(line.order_id.order_duration) - invoiced
                
                # Control how much were invoiced and if 100% of line.price_unit is invoiced:
                if remains_to_invoice <= 0:
                    LOGGER.notifyChannel(self._name, netsvc.LOG_DEBUG, 'All invoices for line "%s" order - %s are created' % (line.name, line.order_id.name))
    
                    sale_order_line_obj.write(cr, uid, [line.id], {'invoiced': True})
                else:
                    # Make an invoice and add a new line in account.invoice
                    LOGGER.notifyChannel(self._name, netsvc.LOG_DEBUG, 'Adding new invoice for line "%s" (order - %s)' % (line.name, line.order_id.name))
                    if not line.order_id.id in invoices:
                        invoices[line.order_id.id] = []
                    
                    # Create account.invoice.line:
                    # This function writes total price and not just installment
                    # It also set 'invoiced' to True
                    line_id = sale_order_line_obj.invoice_line_create(cr, uid, [line.id])
                    
                    # Adjust price_unit of invoice.line
                    self.adjustPrice(cr, uid, line, line_id, remains_to_invoice, invoice_date['period'])
                    
                    for lid in line_id:
                        invoices[line.order_id.id].append((line, lid))
                
            for result in invoices.values():
                order = result[0][0].order_id
                il = map(lambda x: x[1], result)
                res = make_invoice(order, il, invoice_date)
                
                cr.execute('INSERT INTO sale_order_invoice_rel \
                        (order_id, invoice_id) values (%s, %s)', (order.id, res))
                #action_invoice_create(cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception'], date_inv = False, context=None)

    def suspend(self, cr, uid, ids, context):
        wf_service = netsvc.LocalService('workflow')
        account_invoice_obj = self.pool['account.invoice']
        sale_order_line_obj = self.pool['sale.order.line']

        for order in self.browse(cr, uid, ids, context):
            LOGGER.notifyChannel(self._name, netsvc.LOG_INFO, 'Suspending order {0}'.format(order.name))
            if order.have_subscription:
                invoices2cancel = account_invoice_obj.search(cr, uid, [('type', '=', 'out_invoice'), ('origin', '=', order.name)])
                for invoice in account_invoice_obj.browse(cr, uid, invoices2cancel, context):
                    if invoice.state == 'draft':
                        print "canceling invoice {0} ({1})...".format(invoice.name, invoice.id)
                        wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_cancel', cr)
                        account_invoice_obj.unlink(cr, uid, invoice.id, context)

                for line in order.order_line:
                    if line.product_id.subscription:
                        invoiced = sale_order_line_obj.amount_invoiced(cr, uid, line) or 0
                        if invoiced < line.price_subtotal:
                            sale_order_line_obj.write(cr, uid, line.id, {'invoiced': False}, context)

        self.write(cr, uid, ids, {'state': 'suspended'})
        return True

    def reactivate(self, cr, uid, ids, context):
        print "Reactivating..."

        for order in self.browse(cr, uid, ids, context):
            LOGGER.notifyChannel(self._name, netsvc.LOG_INFO, 'Reactivating order {0}'.format(order.name))
            self.auto_invoice(cr, uid, order.id, context=None)

        self.write(cr, uid, ids, {'state': 'progress'})

        return True

    # def close(self, cr, uid, ids, context):
    #     """
    #     The button "Close" is visible only if order is already suspended. It will
    #     cancel order if there are no invoices or set 'done' if there are any
    #     """
    #
    #     wf_service = netsvc.LocalService('workflow')
    #     sale_order_line_obj = self.pool['sale.order.line']
    #     invoiced = 0
    #     for order in self.browse(cr, uid, ids, context):
    #         LOGGER.notifyChannel(self._name, netsvc.LOG_INFO, 'Closing order {0}'.format(order.name))
    #         for line in order.order_line:
    #             if line.product_id.subscription:
    #                 invoiced += sale_order_line_obj.amount_invoiced(cr, uid, line) or 0
    #
    #         pdb.set_trace()
    #         if invoiced:
    #             # TODO: Set done
    #             # Can't cancel order with invoices!!!
    #             wf_service.trg_validate(uid, 'sale.order', order.id, 'cancel', cr)
    #             wf_service.trg_validate(uid, 'sale.order', order.id, 'ship_corrected', cr)
    #
    #             # wf_service.trg_validate(uid, 'sale.order', order.id, 'invoice_corrected', cr)
    #             # wf_service.trg_validate(uid, 'sale.order', order.id, 'all_lines', cr)
    #             print 'Done'
    #         else:
    #             wf_service.trg_validate(uid, 'sale.order', order.id, 'cancel', cr)
    #     return True
