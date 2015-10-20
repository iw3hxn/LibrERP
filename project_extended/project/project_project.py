# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2013 Didotech Srl. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################.

from openerp.osv import orm, fields
import decimal_precision as dp


class project_task(orm.Model):
    _inherit = 'project.project'

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        spent_group = self.pool['res.groups'].user_in_group(cr, uid, uid, 'project.can_modify_prices', context=context)
        for project in self.browse(cr, uid, ids, context):
            # import pdb; pdb.set_trace()
            if spent_group:
                effective_hours = project.total_spent
                planned_hours = project.total_sell_service
            else:
                effective_hours = project.effective_hours
                planned_hours = project.planned_hours
            if effective_hours < (planned_hours * 0.8):  # < 80%
                value[project.id] = 'green'
            elif effective_hours < planned_hours:
                value[project.id] = 'orange'
            elif effective_hours == planned_hours:
                value[project.id] = 'black'
            else:
                value[project.id] = 'red'

            # ore effettive <= previste verde altrimenti rosso

        return value


    def _task_count(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = dict.fromkeys(ids, 0)
        ctx = context.copy()
        ctx['active_test'] = False
        task_ids = self.pool['project.task'].search(cr, uid, [('project_id', 'in', ids)], context=ctx)
        for task in self.pool['project.task'].browse(cr, uid, task_ids, context):
            if task.state != 'done':
                res[task.project_id.id] += 1
        return res
    
    #def _total_sale(self, cr, uid, ids, field_name, arg, context=None):
    #    if context is None:
    #        context = {}
    #    res = {}
    #    projects = self.browse(cr, uid, ids)
    #    for project_id in projects:
    #        sale_ids = self.pool['sale.order'].search(cr, uid, [('project_id', '=', project_id.analytic_account_id.id)], context=context)
    #        res[project_id.id] = {
    #            'total_sell': 0.0,
    #        }
    #        for sale in self.pool['sale.order'].browse(cr, uid, sale_ids, context):
    #            res[project_id.id]['total_sell'] += sale.amount_untaxed
    #    return res

    def _total_account(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = {}
        projects = self.browse(cr, uid, ids, context=context)
        for project_id in projects:
            account_ids = self.pool['account.analytic.line'].search(cr, uid, [('account_id', '=', project_id.analytic_account_id.id)], context=context)
            sale_ids = self.pool['sale.order'].search(cr, uid, [('project_id', '=', project_id.analytic_account_id.id), ('state', 'not in', ['draft'])], context=context)
            
            res[project_id.id] = {
                'total_spent': 0.0,
                'total_invoice': 0.0,
                'total_sell': 0.0,
                'total_sell_service': 0.0,
            }
            for account in self.pool['account.analytic.line'].browse(cr, uid, account_ids, context):
                if account.amount > 0:
                    res[project_id.id]['total_invoice'] += account.amount
                else:
                    res[project_id.id]['total_spent'] += abs(account.amount)
            for sale in self.pool['sale.order'].browse(cr, uid, sale_ids, context):
                res[project_id.id]['total_sell'] += sale.amount_untaxed
                for sale_line in sale.order_line:
                    if sale_line.product_id and sale_line.product_id.type == 'service':
                        res[project_id.id]['total_sell_service'] += sale_line.price_subtotal
        return res
    
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            if record.partner_id:
                name = record.name + ' : ' + record.partner_id.name
            else:
                name = record.name
            if len(name) > 45:
                name = name[:45] + '...'
            res.append((record.id, name))
        return res
    
    _columns = {
        'row_color': fields.function(get_color, string = 'Row color', type='char', readonly=True, method=True),
        'task_count': fields.function(_task_count, type='integer', string="Open Tasks"),
        'total_sell': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Sell Amount"),
        'total_sell_service': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Service Sell Amount"),
        'total_spent': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Spent Amount"),
        'total_invoice': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Invoice Amount"),
    }
