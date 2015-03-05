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
    }
    
    def compute(self, cr, uid, id, value, value_tax=False, date_ref=False, context=None):
        '''Function overwritten for check also month values and 2 months with no payments
        allowed for the partner.'''
        result = []
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        obj_precision = self.pool['decimal.precision']
        prec = obj_precision.precision_get(cr, uid, 'Account')
        for line in pt.line_ids:
            if line.value == 'tax':
                amt = round(line.value_amount * value_tax, prec)
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
