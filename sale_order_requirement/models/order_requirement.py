# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Didotech SRL
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

from tools.translate import _
from datetime import date, datetime

from openerp.osv import orm, fields
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class order_requirement(orm.Model):

    _name = 'order.requirement'

    def _get_day(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for order_requirement in self.browse(cr, uid, ids, context=context):
            res[order_requirement.id] = {
                'week_nbr': False,
            }
            if not order_requirement.date:
                continue

            start_date = datetime.strptime(order_requirement.date, DEFAULT_SERVER_DATE_FORMAT)
            start_date = date(start_date.year, start_date.month, start_date.day)

            # mese in italiano start_date.strftime('%B').capitalize()
            res[order_requirement.id] = {
                'week_nbr': start_date.isocalendar()[1],
                'month': int(start_date.strftime("%m")),
            }

        return res

    _rec_name = 'sale_order_id'

    _columns = {
        'date': fields.date('Data'),
        'sale_order_id': fields.many2one('sale.order', 'Order', required=True),
        'customer_id': fields.related('sale_order_id', 'partner_id', type='many2one', relation='res.partner', string='Customer', store=False),
        'user_id': fields.many2one('res.users', 'User'),
        'week_nbr': fields.function(_get_day, method=True, multi='day_of_week', type="integer", string="Week Number", store={
            'order.requirement': (lambda self, cr, uid, ids, c={}: ids, ['date'], 30),
        }),
        'month': fields.function(_get_day, type='integer', string='Month', method=True, multi='day_of_week', store={
            'order.requirement': (lambda self, cr, uid, ids, c={}: ids, ['date_start'], 30),
        }),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Confirmed'),
            ('cancel', 'Cancelled')
        ], 'Order State', readonly=True),
        'order_requirement_line_ids': fields.one2many('order.requirement.line', 'order_requirement_id', 'Order Lines', readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'note': fields.text('Note')
    }

    _defaults = {
        'date': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }

    def set_state_done(self, cr, uid, ids, context):
        # TODO

        self.write(cr, uid, ids, {'state': 'done'})
