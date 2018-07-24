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
