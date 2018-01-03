# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Micronaet SRL (<http://www.micronaet.it>).
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
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
import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from openerp.osv import fields, orm
from tools.translate import _

PAYMENT_TERM_TYPE_SELECTION = [
    ('BB', 'Bonifico Bancario'),
    ('BP', 'Bonifico Postale'),
    ('RD', 'Rimessa Diretta'),
    ('RB', 'Ricevuta Bancaria'),
    ('F4', 'F24'),
    ('PP', 'Paypal'),
    ('CC', 'Carta di Credito'),
    ('CO', 'Contrassegno'),
    ('CN', 'Contanti'),
    ('SD', 'Sepa DD'),
]


class account_payment_term_line(orm.Model):
    ''' Add extra field for manage commercial payments
    '''
    _name = "account.payment.term.line"
    _inherit = "account.payment.term.line"

    _columns = {
        'months': fields.integer(
            'Number of month', required=False,
            help="Number of month to add before computation of the day of "
                 "month. If Date=15-01, Number of month=1, Day of Month=-1, "
                 "then the due date is 28-02. If compiled, there is no "
                 "need to compile the field Days."),
        'value': fields.selection([('procent', 'Percent'),
                           ('balance', 'Balance'),
                           ('fixed', 'Fixed Amount'),
                           ('tax', 'Tax Amount'),
                           ], 'Valuation',
                           required=True, help="""Select here the kind of valuation related to this payment term line. 
                           Note that you should have your last line with the type 'Balance' to ensure that the whole 
                           amount will be threated."""),
    }
    _defaults = {
        'days': 0,
        'months': 0,
    }


class account_payment_term(orm.Model):
    ''' Overwrite compute method, add month check and 2 months which payment
    can be delayed to the next month.'''
    _name = "account.payment.term"
    _inherit = "account.payment.term"

    _columns = {
        'month_to_be_delayed1': fields.integer(
            'First month without payments', required=False,
            help="First month with no payments allowed."),
        'days_to_be_delayed1': fields.integer(
            'Days of delay for first month', required=False, help="Number of days of delay"
            " for first month without payments."),
        'min_day_to_be_delayed1': fields.integer('First date from which payment will be'
            ' delayed.'),
        'month_to_be_delayed2': fields.integer(
            'Second month without payments', required=False,
            help="Second month with no payments allowed."),
        'days_to_be_delayed2': fields.integer(
            'Days of delay for second month', required=False, help="Number of days of delay"
            " for second month without payments."),
        'min_day_to_be_delayed2': fields.integer('Second date from which payment will be'
            ' delayed.'),
        'type': fields.selection(PAYMENT_TERM_TYPE_SELECTION, "Type of payment"),
    }

    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        '''Function overwritten for check also month values and 2 months with no payments
        allowed for the partner.'''
        result = []
        context = context or {}
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        amount_tax = context.get('amount_tax', 0.0)
        obj_precision = self.pool['decimal.precision']
        prec = obj_precision.precision_get(cr, uid, 'Account')
        for line in pt.line_ids:
            if line.value == 'tax':
                amt = round(line.value_amount * amount_tax, prec)
                value -= amt
            elif line.value == 'fixed':
                amt = round(line.value_amount, prec)
            elif line.value == 'procent':
                amt = round(value * line.value_amount, prec)
            elif line.value == 'balance':
                amt = round(amount, prec)

            if amt:
                if line.months != 0:  # commercial months
                    next_date = (
                        datetime.strptime(date_ref, '%Y-%m-%d') +
                        relativedelta(months=line.months))
                    if line.days2 < 0:
                        next_first_date = next_date + relativedelta(
                            day=1, months=1)  # Getting 1st of next month
                        next_date = next_first_date + relativedelta(
                            days=line.days2)
                        if next_date.month == pt.month_to_be_delayed1 and \
                                next_date.day >= pt.min_day_to_be_delayed1:
                            next_date = next_first_date + relativedelta(
                                day=pt.days_to_be_delayed1)
                        if next_date.month == pt.month_to_be_delayed2 and \
                                next_date.day >= pt.min_day_to_be_delayed2:
                            next_date = next_first_date + relativedelta(
                                day=pt.days_to_be_delayed2)
                    if line.days2 > 0:
                        next_date += relativedelta(day=line.days2, months=1)
                        if next_date.month == pt.month_to_be_delayed1 and \
                                next_date.day >= pt.min_day_to_be_delayed1:
                            next_date += relativedelta(
                                day=pt.days_to_be_delayed1, months=1)
                        if next_date.month == pt.month_to_be_delayed2 and \
                                next_date.day >= pt.min_day_to_be_delayed2:
                            next_date += relativedelta(
                                day=pt.days_to_be_delayed2, months=1)
                    result.append((next_date.strftime('%Y-%m-%d'), amt))
                else:
                    next_date = (datetime.strptime(date_ref, '%Y-%m-%d')
                                 + relativedelta(days=line.days))
                    if line.days2 < 0:
                        next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                        next_date = next_first_date + relativedelta(days=line.days2)
                        if next_date.month == pt.month_to_be_delayed1 and \
                                next_date.day >= pt.min_day_to_be_delayed1:
                            next_date = next_first_date + relativedelta(
                                day=pt.days_to_be_delayed1)
                        if next_date.month == pt.month_to_be_delayed2 and \
                                next_date.day >= pt.min_day_to_be_delayed2:
                            next_date = next_first_date + relativedelta(
                                day=pt.days_to_be_delayed2)
                    if line.days2 >= 0:
                        if line.days2 > 0:
                            next_date += relativedelta(day=line.days2, months=1)
                        if next_date.month == pt.month_to_be_delayed1 and \
                                next_date.day >= pt.min_day_to_be_delayed1:
                            next_date += relativedelta(
                                day=pt.days_to_be_delayed1, months=1)
                        if next_date.month == pt.month_to_be_delayed2 and \
                                next_date.day >= pt.min_day_to_be_delayed2:
                            next_date += relativedelta(
                                day=pt.days_to_be_delayed2, months=1)
                    result.append((next_date.strftime('%Y-%m-%d'), amt))
                amount -= amt
        return result

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def onchange_payment_term_date_invoice(self, cr, uid, ids, payment_term_id, date_invoice):
        if not payment_term_id:
            return {}
        res = {}
        context = self.pool['res.users'].context_get(cr, uid)
        pt_obj = self.pool['account.payment.term']
        ait_obj = self.pool['account.invoice.tax']

        if not date_invoice:
            date_invoice = time.strftime('%Y-%m-%d')

        compute_taxes = ait_obj.compute(cr, uid, ids, context=context)
        amount_tax = 0
        for tax in compute_taxes:
            amount_tax += compute_taxes[tax]['amount']
        context.update({'amount_tax': amount_tax})

        pterm_list = pt_obj.compute(cr, uid, payment_term_id, value=1, date_ref=date_invoice, context=context)

        if pterm_list:
            pterm_list = [line[0] for line in pterm_list]
            pterm_list.sort()
            res = {'value': {'date_due': pterm_list[-1]}}
        else:
            raise orm.except_orm(_('Data Insufficient !'),
                                 _('The payment term of supplier does not have a payment term line!'))
        return res
