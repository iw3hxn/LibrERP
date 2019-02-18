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
from datetime import datetime

from dateutil.relativedelta import relativedelta
from openerp.osv import fields, orm

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


class account_payment_term(orm.Model):
    ''' Overwrite compute method, add month check and 2 months which payment
    can be delayed to the next month.'''
    _name = "account.payment.term"
    _inherit = "account.payment.term"

    _columns = {
        'month_list': fields.char('Month List'),
        'month_day': fields.integer('Day of payment'),
        'tax_exclude': fields.boolean('Tax Exclude'),
        'tax_day': fields.integer('Tax Day'),
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

    def _get_payment_term_line_vals(self, cr, uid, month_number, month_total_number, days, day2=0, context=None):
        if day2 == -1:
            delta = 'FM'
        elif day2 > 0:
            delta = u'+ {}'.format(day2)
        else:
            delta = ''

        if month_total_number:
            value_amount = float(100.0 / month_total_number) / 100.00
        else:
            value_amount = 1
        vals = {
            'sequence': month_number,
            'name': u'{0} {1}'.format(days, delta),
            'value': 'procent',
            'days': days,
            'days2': day2,
            'value_amount': value_amount
        }
        if month_number == month_total_number:
            vals.update({
                'value': 'balance',
                'value_amount': 0
            })
        return vals

    def create(self, cr, uid, value, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if 'month_list' in value and not value.get('line_ids', False):
            month_list = []
            if value.get('month_list'):
                month_list = [int(b) for b in value.get('month_list').replace('/', ',').split(',') if b]
            month__total_number = len(month_list)
            lines_vals = []
            if value.get('tax_exclude', False):
                tax_vals = self._get_payment_term_line_vals(cr, uid, 0, 0, value.get('tax_day' or 0), 0, context)
                tax_vals.update({
                    'value': 'tax',
                    'value_amount': 1
                })
                lines_vals.append(tax_vals)
            for month in month_list:
                lines_vals.append(self._get_payment_term_line_vals(cr, uid, month_list.index(month) + 1, month__total_number, month, value.get('month_day' or 0), context))
            value['line_ids'] = [(0, False, line) for line in lines_vals]
        res = super(account_payment_term, self).create(cr, uid, value, context)
        return res

    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        '''Function overwritten for check also month values and 2 months with no payments
        allowed for the partner.'''
        result = []
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        sign = lambda x: (1, -1)[x < 0]
        amount_tax = context.get('amount_tax', 0.0)
        obj_precision = self.pool['decimal.precision']
        prec = obj_precision.precision_get(cr, uid, 'Account')
        for line in pt.line_ids:
            if line.value == 'tax':
                amt = sign(value) * round(line.value_amount * amount_tax, prec)
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

