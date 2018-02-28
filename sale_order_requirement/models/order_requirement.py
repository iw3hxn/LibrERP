# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from tools.translate import _
from datetime import date, datetime

from openerp.osv import orm, fields
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class order_requirement(orm.Model):

    _name = 'order.requirement'

    def _get_day(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for requirement in self.browse(cr, uid, ids, context=context):
            res[requirement.id] = {
                'week_nbr': False,
            }
            if not requirement.date:
                continue

            start_date = datetime.strptime(requirement.date, DEFAULT_SERVER_DATE_FORMAT)
            start_date = date(start_date.year, start_date.month, start_date.day)

            # mese in italiano start_date.strftime('%B').capitalize()
            res[requirement.id] = {
                'week_nbr': start_date.isocalendar()[1],
                'month': int(start_date.strftime("%m")),
            }

        return res

    _rec_name = 'sale_order_id'

    _columns = {
        'date': fields.date('Data'),
        'sale_order_id': fields.many2one('sale.order', 'Order', required=True, ondelete='cascade'),
        'client_order_ref': fields.related('sale_order_id', 'client_order_ref', type='char', string="Customer Reference"),
        'customer_id': fields.related('sale_order_id', 'partner_id', type='many2one', relation='res.partner', string='Customer', store=False),
        'user_id': fields.many2one('res.users', 'User'),
        'week_nbr': fields.function(_get_day, method=True, multi='day_of_week', type="integer", string="Week Number", store={
            'order.requirement': (lambda self, cr, uid, ids, c={}: ids, ['date'], 30),
        }),
        'month': fields.function(_get_day, type='integer', string='Month', method=True, multi='day_of_week', store={
            'order.requirement': (lambda self, cr, uid, ids, c={}: ids, ['date'], 30),
        }),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Confirmed'),
            ('cancel', 'Cancelled')
        ], 'Order State', readonly=True),
        'order_requirement_line_ids': fields.one2many('order.requirement.line', 'order_requirement_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'note': fields.text('Order Note'),
        'internal_note': fields.related('sale_order_id', 'picking_ids', 'internal_note', type='text', string='Internal Note'),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'production_product_id': fields.related('order_requirement_line_ids', 'temp_mrp_bom_ids', 'product_id', type='many2one', relation='product.product',
                                     string='Product Production'),
        'product_id': fields.related('order_requirement_line_ids', 'product_id', type='many2one', relation='product.product',
                                     string='Product'),
        'new_product_id': fields.related('order_requirement_line_ids', 'new_product_id', type='many2one', relation='product.product',
                                     string='Choosen Product'),
    }

    _defaults = {
        'date': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }

    _order = 'date desc'

    def set_state_draft(self, cr, uid, ids, context):
        for order in self.browse(cr, uid, ids, context):
            for line in order.order_requirement_line_ids:
                if line.state != 'draft':
                    print line
                    # todo cancel purchase order and purchase production order

    # def set_state_done(self, cr, uid, ids, context):
        # TODO set_state_done, now commented in view
        # pass
        # self.write(cr, uid, ids, {'state': 'done'})
