# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2016 Didotech Srl. (<http://www.didotech.com>)
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
from datetime import datetime


class project_project(orm.Model):
    _inherit = 'project.project'

    def get_color(self, cr, uid, ids, field_name, arg, context):
        start_time = datetime.now()
        value = {}
        total_spent_group = self.pool['res.groups'].user_in_group(cr, uid, uid, 'project.can_modify_prices', context=context)
        service_spent_group = self.pool['res.groups'].user_in_group(cr, uid, uid, 'project.color_service_spent_amount', context=context)

        for project in self.browse(cr, uid, ids, context):
            if total_spent_group:
                effective_hours = project.total_spent
                planned_hours = project.total_sell
            elif service_spent_group:
                effective_hours = project.total_service_spent
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
        end_time = datetime.now()
        duration_seconds = (end_time - start_time)
        duration = '{sec}'.format(sec=duration_seconds)
        print duration
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
    
    # def _total_sale(self, cr, uid, ids, field_name, arg, context=None):
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
        for project_id in self.browse(cr, uid, ids, context=context):
            res[project_id.id] = {
                'total_spent': 0.0,
                'total_invoice': 0.0,
                'total_sell': 0.0,
                'total_sell_service': 0.0,
                'total_service_spent': 0.0,
            }
            # import pdb; pdb.set_trace()
            account_ids = self.pool['account.analytic.line'].search(cr, uid, [('account_id', '=', project_id.analytic_account_id.id), ('invoice_id', '!=', False)], context=context)

            if account_ids:
                cr.execute("""
                    SELECT COALESCE(SUM(amount))
                    FROM account_analytic_line
                    WHERE account_analytic_line.id IN ({account_ids})
                """.format(account_ids=', '.join([str(account_id) for account_id in account_ids])))
                total_invoice = cr.fetchone()[0] or 0.0
                res[project_id.id]['total_invoice'] = total_invoice

            account_ids = self.pool['account.analytic.line'].search(cr, uid, [('account_id', '=', project_id.analytic_account_id.id), ('invoice_id', '=', False)],
                                                                        context=context)
            if account_ids:
                cr.execute("""
                    SELECT ABS(COALESCE(SUM(amount)))
                    FROM account_analytic_line
                    WHERE account_analytic_line.id IN ({account_ids}) AND account_analytic_line.amount < 0
                """.format(account_ids=', '.join([str(account_id) for account_id in account_ids])))
                total_spent = cr.fetchone()[0] or 0.0
                res[project_id.id]['total_spent'] = total_spent

                account_ids = self.pool['account.analytic.line'].search(cr, uid, [('account_id', '=', project_id.analytic_account_id.id), ('product_id.type', '=', 'service'), ('invoice_id', '=', False)], context=context)
                if account_ids:
                    cr.execute("""
                        SELECT ABS(COALESCE(SUM(amount)))
                        FROM account_analytic_line
                        WHERE account_analytic_line.id IN ({account_ids}) AND account_analytic_line.amount < 0
                    """.format(account_ids=', '.join([str(account_id) for account_id in account_ids])))
                    total_service_spent = cr.fetchone()[0] or 0.0
                    res[project_id.id]['total_service_spent'] = total_service_spent

            # for account in self.pool['account.analytic.line'].browse(cr, uid, account_ids, context):
            #     if account.amount > 0:
            #         res[project_id.id]['total_invoice'] += account.amount
            #     else:
            #         res[project_id.id]['total_spent'] += abs(account.amount)

            # account_ids = self.pool['account.analytic.line'].search(cr, uid, [('account_id', '=', project_id.analytic_account_id.id), ('product_id.type', '=', 'service')], context=context)
            # for account in self.pool['account.analytic.line'].browse(cr, uid, account_ids, context):
            #     if not account.amount > 0:
            #         res[project_id.id]['total_service_spent'] += abs(account.amount)

            sale_ids = self.pool['sale.order'].search(cr, uid, [
                ('project_id', '=', project_id.analytic_account_id.id),
                ('state', 'not in', ['draft'])
            ], context=context)

            if sale_ids:
                cr.execute("""
                    SELECT COALESCE(SUM(amount_untaxed))
                    FROM sale_order
                    WHERE sale_order.id IN ({sale_ids})
                """.format(sale_ids=', '.join([str(sale_id) for sale_id in sale_ids])))

                total_sell = cr.fetchone()[0] or 0.0
                res[project_id.id]['total_sell'] = total_sell
                cr.execute("""
                    SELECT COALESCE(SUM(price_subtotal))
                    FROM sale_order_line
                    LEFT JOIN product_product ON sale_order_line.product_id = product_product.id
                    LEFT JOIN product_template ON product_product.product_tmpl_id = product_template.id
                    WHERE sale_order_line.order_id IN ({sale_ids})
                    AND product_template.type ILIKE 'service'
                """.format(sale_ids=', '.join([str(sale_id) for sale_id in sale_ids])))
                total_sell_service = cr.fetchone()[0] or 0.0
                res[project_id.id]['total_sell_service'] = total_sell_service

            # for sale in self.pool['sale.order'].browse(cr, uid, sale_ids, context):
            #     res[project_id.id]['total_sell'] += sale.amount_untaxed
            #
            #     for sale_line in sale.order_line:
            #         if sale_line.product_id and sale_line.product_id.type == 'service':
            #             res[project_id.id]['total_sell_service'] += sale_line.price_subtotal
            #
            # if not total_sell == res[project_id.id]['total_sell']:
            #     import pdb; pdb.set_trace()
            # else:
            #     print 'YYYYYYYYY'
            #
            # if not total_sell_service == res[project_id.id]['total_sell_service']:
            #     pdb.set_trace()
            # else:
            #     import pdb;
            #     print 'ZZZZZZZZZ'

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

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):

        project_selection = super(project_project, self).name_search(cr, uid, name, args, operator, context=context,
                                                                     limit=limit)
        if name:
            partner_ids = self.pool['res.partner'].search(cr, uid, [('name', 'ilike', name)])
            if partner_ids:
                if args:
                    relative_project = self.name_search(cr, uid, '', args + [('partner_id', 'in', partner_ids)],
                                                        operator,
                                                        context=context, limit=limit)
                else:
                    relative_project = self.name_search(cr, uid, '', [('partner_id', 'in', partner_ids)], operator,
                                                        context=context, limit=limit)
                if relative_project:
                    project_selection = list(set(project_selection + relative_project))

        # Sort by name
        return sorted(project_selection, key=lambda x: x[1])

    def _get_sale_order(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        sale_order_obj = self.pool['sale.order']
        for project in self.browse(cr, uid, ids, context):
            name = project.name.split('-')[0]
            result[project.id] = sale_order_obj.search(cr, uid, [('name', 'like', name)], context=context)

        return result

    def _get_purchase_order(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        purchase_order_obj = self.pool['purchase.order']

        for project in self.browse(cr, uid, ids, context):
            name = project.name.split('-')[0]
            result[project.id] = purchase_order_obj.search(cr, uid, [('origin', 'ilike', name), ('state', 'not in', ['draft', 'cancel'])], context=context)

        return result

    def _get_project(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool['project.task'].browse(cr, uid, ids, context=context):
            result[line.project_id.id] = True
        return result.keys()

    def _get_project_account(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool['account.analytic.line'].browse(cr, uid, ids, context=context):
            if line.account_id:
                for project in self.pool['project.project'].search(cr, uid, [('analytic_account_id', '=', line.account_id.id)], context=context):
                    result[project] = True
        return result.keys()

    def _get_project_order_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool['sale.order.line'].browse(cr, uid, ids, context=context):
            if line.order_id.project_project:
                result[line.order_id.project_project.id] = True
        return result.keys()

    def _get_project_order(self, cr, uid, ids, context=None):
        result = {}
        for order in self.pool['sale.order'].browse(cr, uid, ids, context=context):
            if order.project_project:
                result[order.project_project.id] = True
        return result.keys()
    
    _columns = {
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True),
        'sale_order_ids': fields.function(_get_sale_order, 'Sale Order', type='one2many', relation="sale.order",
                                          readonly=True, method=True),
        'purchase_order_ids': fields.function(_get_purchase_order, 'Purchase Order', type='one2many', relation="purchase.order",
                                          readonly=True, method=True),
        'task_count': fields.function(_task_count, type='integer', string="Open Tasks", store={
            'project.task': (_get_project, ['state'], 10),
        }, ),
        # 'total_sell': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Sell Amount"),
        # 'total_sell_service': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Service Sell Amount"),
        # 'total_spent': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Spent Amount"),
        # 'total_service_spent': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Service Spent Amount"),
        # 'total_invoice': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Invoice Amount"),
        'total_sell': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'),
                                      multi='sums', string="Sell Amount", store={
                'sale.order': (_get_project_order, ['state'], 50),
                'sale.order.line': (_get_project_order_line, ['price_subtotal'], 50),
            }, ),
        'total_sell_service': fields.function(_total_account, type='float',
                                              digits_compute=dp.get_precision('Sale Price'), multi='sums',
                                              string="Service Sell Amount", store={
                'sale.order': (_get_project_order, ['state'], 50),
                'sale.order.line': (_get_project_order_line, ['price_subtotal'], 50),
            }, ),
        'total_spent': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'),
                                       multi='sums', string="Spent Amount", store={
                'account.analytic.line': (_get_project_account, ['amount'], 60),
            }, ),
        'total_service_spent': fields.function(_total_account, type='float',
                                               digits_compute=dp.get_precision('Sale Price'), multi='sums',
                                               string="Service Spent Amount", store={
                'account.analytic.line': (_get_project_account, ['amount'], 70),
            }, ),
        'total_invoice': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'),
                                         multi='sums', string="Invoice Amount", store={
                'account.analytic.line': (_get_project_account, ['amount'], 80),
            }, ),
    }
