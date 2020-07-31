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

import decimal_precision as dp
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

# locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
from openerp.addons.sale_subscriptions.models.sale_order import ORDER_DURATION


class SaleOrderLine(orm.Model):
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
                if line.product_id.order_duration:
                    ratio = 365 / line.product_id.order_duration or 1
                else:
                    ratio = 1
                k = float(order_obj.get_duration_in_months(line.order_id.order_duration)) / float(order_obj.get_duration_in_months(line.product_id.order_duration))
                res[line.id] = cur_obj.round(cr, uid, cur, (taxes['total'] / ratio) * k)
            else:
                res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        price_subtotal = self._amount_line(cr, uid, ids, field_name, arg, context)
        order_obj = self.pool['sale.order']
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'margin': 0,
                'total_purchase_price': 0,
            }
            price_subtotal_line = price_subtotal[line.id]
            if line.purchase_price:
                total_purchase_price = line.product_uom_qty * line.purchase_price
            elif line.product_id:
                total_purchase_price = line.product_uom_qty * line.product_id.standard_price
            else:
                total_purchase_price = 0
            if line.order_id.have_subscription and line.product_id.subscription:
                k = order_obj.get_duration_in_months(line.order_id.order_duration) / order_obj.get_duration_in_months(line.product_id.order_duration)
                total_purchase_price = total_purchase_price * k
            else:
                total_purchase_price = total_purchase_price

            res[line.id] = {
                'margin': price_subtotal_line - total_purchase_price,
                'total_purchase_price': total_purchase_price,
            }
        return res

    def __init__(self, registry, cr):
        """
            Overwriting _product_margin method and adding state "Suspended"
        """

        super(SaleOrderLine, self).__init__(registry, cr)

        # self._columns['margin']._fnct = self._product_margin

    _columns = {
        'price_unit': fields.float('Unit Price', help="Se abbonamento intero importo nell'anno ", required=True, digits_compute=dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'subscription': fields.related('product_id', 'subscription', type='boolean', string=_('Subscription')),
        'automatically_create_new_subscription': fields.boolean(_('Automatically create new subscription')),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Sale Price'), store={
                                            'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, [], 2),
        },),
        'suspended': fields.boolean(_('Suspended')),
        'partner_id': fields.related('order_id', 'partner_id', 'name', type='char', string=_('Customer'), store=True),
        'order_start_date': fields.related('order_id', 'order_start_date', type='date', string=_('Order Start')),
        'order_duration': fields.related('order_id', 'order_duration', type='selection', string=_('Duration'), selection=ORDER_DURATION),
        'product_duration': fields.related('product_id', 'order_duration', type='selection', string=_('Duration'), selection=ORDER_DURATION),
        'order_end_date': fields.related('order_id', 'order_end_date', type='date', string=_('Order End'), store=True),
        'user_id': fields.related('order_id', 'user_id', 'name', type='char', string=_('Salesman'), store=True),
        'section_id': fields.related('order_id', 'section_id', 'name', type='char', string=_('Sales Team'), store=True),
        'can_activate': fields.boolean("Activate ?"),
        'margin': fields.function(_product_margin, string='Margin', multi='sums', type='float', digits_compute=dp.get_precision('Account'), store={
            'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit', 'product_uos_qty', 'discount', 'purchase_price', 'product_id'], 100),
        }),
        'total_purchase_price': fields.function(_product_margin, multi='sums', type='float', string='Total Cost Price', digits_compute=dp.get_precision('Account'), store={
            'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit', 'product_uos_qty', 'discount', 'purchase_price', 'product_id'], 100),
        }),
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

        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product_id, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context)

        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context)
            res['value']['subscription'] = product.subscription
            if product.subscription:
                if product.order_duration:
                    ratio = 365 / product.order_duration
                else:
                    ratio = 1
                res['value'].update({
                    'price_unit': res['value']['price_unit'] * ratio
                })

        return res

    def action_suspend(self, cr, uid, line_ids, context):
        invoice_line_obj = self.pool['account.invoice.line']
        invoice_obj = self.pool['account.invoice']
        order_to_suspend = []

        suspend_date = datetime.datetime.now()
        updated_invoice_ids = []
        lines = self.browse(cr, uid, line_ids, context=context)
        for line in lines:
            active_order_line_count = 0
            for oline in line.order_id.order_line:
                if not oline.suspended:
                    active_order_line_count += 1
            
            if active_order_line_count == 1:
                order_to_suspend.append(line.order_id.id)
            else:
                line_2_suspend_ids = [line_2_suspend.id for line_2_suspend in lines if line_2_suspend.product_id.subscription]
                self.pool['sale.order.line'].write(cr, uid, line_2_suspend_ids, {'suspended': True}, context)
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
        if abs(remains_to_invoice) <= 0:
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
            sale_order_obj.adjust_price(cr, uid, order_line, invoice_line_ids, remains_to_invoice, invoice_period, context)
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
        return super(SaleOrderLine, self).create(cr, uid, values, context)

    def write(self, cr, uid, ids, values, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if values.get('product_id'):
            product = self.pool['product.product'].browse(cr, uid, values['product_id'], context)
            for order_line in self.browse(cr, uid, ids, context):
                if product.subscription and not order_line.order_id.have_subscription:
                    raise orm.except_orm(_('Error'), _("You've added subscriptable product to an order which has no Payments in Installments"))
        return super(SaleOrderLine, self).write(cr, uid, ids, values, context)

    def action_dummy(self, cr, uid, line_ids, context):
        return True

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        # no reason to sum price_units
        if 'price_unit' in fields:
            fields.remove('price_unit')

        result = super(SaleOrderLine, self).read_group(cr, uid, domain, fields, groupby, offset, limit=limit, context=context, orderby=orderby)

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

