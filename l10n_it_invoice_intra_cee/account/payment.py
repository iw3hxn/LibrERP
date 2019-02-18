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
from openerp.osv import orm


class account_payment_term(orm.Model):
    _inherit = "account.payment.term"

    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        '''Function overwritten for check also month values and 2 months with no payments
        allowed for the partner [account_payment_term_month] and to create a lonely row
        for reverse charge tax.'''
        result = []
        context = context or {}
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        sign = lambda x: (1, -1)[x < 0]
        obj_precision = self.pool['decimal.precision']
        prec = obj_precision.precision_get(cr, uid, 'Account')
        amount_tax = context.get('amount_tax', False)
        # create a lonely line for tax value
        if context.get('reverse_charge', False) and amount_tax and amount_tax != 0.0:
            value = (abs(value) - abs(amount_tax)) * (value / abs(value))
            amount = value
            result.append((date_ref, amount_tax * (value / abs(value))))

        for line in pt.line_ids:
            if line.value == 'tax':
                if context.get('reverse_charge', False):
                    continue
                else:
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
                    if context.get('reverse_charge', False) and amount_tax and amount_tax != 0.0:
                        if (next_date.strftime('%Y-%m-%d')) == date_ref:
                            next_date += relativedelta(days=1)
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
                    if context.get('reverse_charge', False) and amount_tax and amount_tax != 0.0:
                        if (next_date.strftime('%Y-%m-%d')) == date_ref:
                            next_date += relativedelta(days=1)
                    result.append((next_date.strftime('%Y-%m-%d'), amt))
                amount -= amt
        return result
