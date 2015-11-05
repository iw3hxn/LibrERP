# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2015 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_UP
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class sale_shop(orm.Model):
    _inherit = "sale.shop"

    def action_prev(self, cr, uid, ids, context):
        shop = self.browse(cr, uid, ids, context)[0]
        date_from = (datetime.strptime(shop.date_from, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=-1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        date_to = (datetime.strptime(shop.date_to, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=-1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        shop.write({'date_from': date_from, 'date_to': date_to})
        return True

    def action_next(self, cr, uid, ids, context):
        shop = self.browse(cr, uid, ids, context)[0]
        date_from = (datetime.strptime(shop.date_from, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=+1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        date_to = (datetime.strptime(shop.date_to, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=+1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        shop.write({'date_from': date_from, 'date_to': date_to})
        return True

    def _compute_analysis(self, cr, uid, ids, name, args, context=None):
        res = {}

        for shop in self.browse(cr, uid, ids, context):

            new_args = [('shop_id', '=', shop.id)]
            section_id = context.get('section_id', shop.section_id) or False
            date_from = context.get('date_from', shop.date_from) or False
            date_to = context.get('date_to', shop.date_to) or False

            if section_id:
                new_args.append(('section_id', '=', section_id))
            if date_from:
                new_args.append(('date_order', '>=', date_from))
            if date_to:
                new_args.append(('date_order', '<=', date_to))

            sale_order_ids = self.pool['sale.order'].search(cr, uid, new_args, context=context)

            amount_draft = 0.0
            amount_wait = 0.0
            amount_done = 0.0
            amount_lost = 0.0

            for sale in self.pool['sale.order'].browse(cr, uid, sale_order_ids, context):
                if sale.state in ['draft', 'wait_technical_validation', 'wait_manager_validation', 'send_to_customer']:
                    amount_draft += sale.amount_untaxed
                elif sale.state in ['wait_customer_validation']:
                    amount_wait += sale.amount_untaxed
                elif sale.state in ['manual', 'progress', 'done']:
                    amount_done += sale.amount_untaxed
                elif sale.state in ['cancel']:
                    amount_lost += sale.amount_untaxed

            amount_total = amount_draft + amount_wait + amount_done + amount_lost
            res[shop.id] = {
                'amount_draft': amount_draft,
                'amount_wait': amount_wait,
                'amount_done': amount_done,
                'amount_lost': amount_lost,
                'amount_total': amount_total,
                'precent_draft': amount_total and amount_draft / amount_total * 100 or 0,
                'precent_wait': amount_total and amount_wait / amount_total * 100 or 0,
                'precent_done': amount_total and amount_done / amount_total * 100 or 0,
                'precent_lost': amount_total and amount_lost / amount_total * 100 or 0,
            }

        return res

    _columns = {
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team'),
        'amount_draft': fields.function(_compute_analysis, type='float', string='In Deploy', multi='amount_draft', context="{'date_from': date_from, 'date_to': date_to, 'section_id': section_id, 'shop_id': self }"),
        'amount_wait': fields.function(_compute_analysis, type='float', string='Customer Wait', multi='amount_draft', context="{'date_from': date_from, 'date_to': date_to, 'section_id': section_id, 'shop_id': self }"),
        'amount_done': fields.function(_compute_analysis, type='float', string='Done', multi='amount_draft', context="{'date_from': date_from, 'date_to': date_to, 'section_id': section_id, 'shop_id': self }"),
        'amount_lost': fields.function(_compute_analysis, type='float', string='Lost', multi='amount_draft', context="{'date_from': date_from, 'date_to': date_to, 'section_id': section_id, 'shop_id': self }"),
        'amount_total': fields.function(_compute_analysis, type='float', string='Total Period', multi='amount_draft', context="{'date_from': date_from, 'date_to': date_to, 'section_id': section_id, 'shop_id': self }"),
        'precent_draft': fields.function(_compute_analysis, type='float', string='% Deploy', multi='amount_draft', context="{'date_from': date_from, 'date_to': date_to, 'section_id': section_id, 'shop_id': self }"),
        'precent_wait': fields.function(_compute_analysis, type='float', string='% Wait', multi='amount_draft', context="{'date_from': date_from, 'date_to': date_to, 'section_id': section_id, 'shop_id': self }"),
        'precent_done': fields.function(_compute_analysis, type='float', string='% Done', multi='amount_draft', context="{'date_from': date_from, 'date_to': date_to, 'section_id': section_id, 'shop_id': self }"),
        'precent_lost': fields.function(_compute_analysis, type='float', string='% Lost', multi='amount_draft', context="{'date_from': date_from, 'date_to': date_to, 'section_id': section_id, 'shop_id': self }"),
    }
