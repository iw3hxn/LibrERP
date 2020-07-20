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

import logging
from datetime import datetime

import decimal_precision as dp
from openerp.osv import orm, fields
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ProjectProject(orm.Model):
    _inherit = 'project.project'

    # def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
    #     # order by name
    #     res = super(project_project, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)
    #     if count:
    #         return res
    #     if res:
    #         cr.execute("""SELECT
    #                 project_project.id
    #             FROM
    #                 project_project,
    #                 account_analytic_account
    #             WHERE
    #                 project_project.analytic_account_id = account_analytic_account.id AND
    #                 project_project.id in ({project_ids})
    #             ORDER BY
    #               account_analytic_account.name ASC
    #         """.format(project_ids=', '.join([str(project_id) for project_id in res])))
    #         sql = cr.fetchall()
    #         return [(r[0]) for r in sql]
    #     else:
    #         return res

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        cr.execute("""SELECT 
                project_project.analytic_account_id
            FROM 
                public.project_project
            WHERE
                project_project.id in ({project_ids}) 
        """.format(project_ids=', '.join([str(project_id) for project_id in ids])))
        sql = cr.fetchall()
        account_analytic_account_ids = list(set([(r[0]) for r in sql]))
        if self.pool['account.analytic.line'].search(cr, uid, [('account_id', 'in', account_analytic_account_ids)], context=context):
            raise orm.except_orm(
                _('Error'),
                _('There are same analytic line'))

        res = super(ProjectProject, self).unlink(cr, uid, ids, context)
        self.pool['account.analytic.account'].unlink(cr, uid, account_analytic_account_ids, context)
        return res

    def color_hook(self, cr, uid, ids, value, context):
        return value

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
        res = self.color_hook(cr, uid, ids, value, context) # hook function for possible extention
        end_time = datetime.now()
        duration_seconds = (end_time - start_time)
        duration = '{sec}'.format(sec=duration_seconds)
        _logger.info(u'Project Color get in {duration}'.format(duration=duration))
        return res

    def _task_count(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = dict.fromkeys(ids, 0)
        ctx = context.copy()
        ctx['active_test'] = False
        # task_ids = self.pool['project.task'].search(cr, uid, [('project_id', 'in', ids)], context=ctx)
        task_ids = self.pool['project.task'].search(cr, uid, [('project_id', 'in', ids), ('state', 'not in', ['done', 'cancelled'])], context=ctx)
        for task in self.pool['project.task'].browse(cr, uid, task_ids, context):
            # if task.state != 'done':
            res[task.project_id.id] += 1
        return res

    def _get_attached_docs(self, cr, uid, ids, field_name, arg, context):
        res = {}
        attachment = self.pool.get('ir.attachment')
        task = self.pool.get('project.task')
        for id in ids:
            project_attachments = attachment.search(cr, uid,
                                                    [('res_model', '=', 'project.project'), ('res_id', '=', id)],
                                                    context=context, count=True)
            task_ids = task.search(cr, uid, [('project_id', '=', id)], context=context)
            task_attachments = attachment.search(cr, uid,
                                                 [('res_model', '=', 'project.task'), ('res_id', 'in', task_ids)],
                                                 context=context, count=True)
            res[id] = (project_attachments or 0) + (task_attachments or 0)
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

    def _sale_order_search_vals_for_total_account(self, cr, uid, project, context):
        return [
            ('project_id', '=', project.analytic_account_id.id),
            ('state', 'not in',
             ['draft', 'wait_technical_validation', 'wait_manager_validation', 'send_to_customer',
              'wait_customer_validation', 'wait_supervisor_validation', 'cancel'])
        ]

    def _total_account(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for project in self.browse(cr, uid, ids, context=context):
            res[project.id] = {
                'total_spent': 0.0,
                'total_invoice': 0.0,
                'total_sell': 0.0,
                'total_sell_service': 0.0,
                'total_service_spent': 0.0,
            }
            # import pdb; pdb.set_trace()
            account_id = project.analytic_account_id.id
            account_ids = self.pool['account.analytic.line'].search(cr, uid, [('account_id', '=', account_id), ('invoice_id', '!=', False)], context=context)
            if account_ids:
                cr.execute("""
                    SELECT COALESCE(SUM(amount))
                    FROM account_analytic_line
                    WHERE account_analytic_line.id IN ({account_ids})
                """.format(account_ids=', '.join([str(account) for account in account_ids])))
                total_invoice = cr.fetchone()[0] or 0.0
                res[project.id]['total_invoice'] = total_invoice

            account_ids = self.pool['account.analytic.line'].search(cr, uid, [('account_id', '=', account_id), ('invoice_id', '=', False)], context=context)
            if account_ids:
                cr.execute("""
                    SELECT ABS(COALESCE(SUM(amount)))
                    FROM account_analytic_line
                    WHERE account_analytic_line.id IN ({account_ids}) AND account_analytic_line.amount < 0
                """.format(account_ids=', '.join([str(account) for account in account_ids])))
                total_spent = cr.fetchone()[0] or 0.0
                res[project.id]['total_spent'] = total_spent

                account_ids = self.pool['account.analytic.line'].search(cr, uid, [('account_id', '=', account_id), ('product_id.type', '=', 'service'), ('invoice_id', '=', False)], context=context)
                if account_ids:
                    cr.execute("""
                        SELECT ABS(COALESCE(SUM(amount)))
                        FROM account_analytic_line
                        WHERE account_analytic_line.id IN ({account_ids}) AND account_analytic_line.amount < 0
                    """.format(account_ids=', '.join([str(account) for account in account_ids])))
                    total_service_spent = cr.fetchone()[0] or 0.0
                    res[project.id]['total_service_spent'] = total_service_spent

            # for account in self.pool['account.analytic.line'].browse(cr, uid, account_ids, context):
            #     if account.amount > 0:
            #         res[project_id.id]['total_invoice'] += account.amount
            #     else:
            #         res[project_id.id]['total_spent'] += abs(account.amount)

            # account_ids = self.pool['account.analytic.line'].search(cr, uid, [('account_id', '=', project_id.analytic_account_id.id), ('product_id.type', '=', 'service')], context=context)
            # for account in self.pool['account.analytic.line'].browse(cr, uid, account_ids, context):
            #     if not account.amount > 0:
            #         res[project_id.id]['total_service_spent'] += abs(account.amount)

            sale_order_search_vals = self._sale_order_search_vals_for_total_account(cr, uid, project, context)

            sale_ids = self.pool['sale.order'].search(cr, uid, sale_order_search_vals, context=context)

            if sale_ids:
                cr.execute("""
                    SELECT COALESCE(SUM(amount_untaxed))
                    FROM sale_order
                    WHERE sale_order.id IN ({sale_ids})
                """.format(sale_ids=', '.join([str(sale_id) for sale_id in sale_ids])))

                total_sell = cr.fetchone()[0] or 0.0
                res[project.id]['total_sell'] = total_sell
                cr.execute("""
                    SELECT COALESCE(SUM(price_subtotal))
                    FROM sale_order_line
                    LEFT JOIN product_product ON sale_order_line.product_id = product_product.id
                    LEFT JOIN product_template ON product_product.product_tmpl_id = product_template.id
                    WHERE sale_order_line.order_id IN ({sale_ids})
                    AND product_template.type ILIKE 'service'
                """.format(sale_ids=', '.join([str(sale_id) for sale_id in sale_ids])))
                total_sell_service = cr.fetchone()[0] or 0.0
                res[project.id]['total_sell_service'] = total_sell_service

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
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not len(ids):
            return []
        res = []
        for project in self.read(cr, uid, ids, ['name', 'partner_id'], context):
            name = project['name']
            if project['partner_id']:
                name += ' : ' + project['partner_id'][1]
            res.append((project['id'], name))
        # for project in self.browse(cr, uid, ids, context=context):
        #     if project.partner_id:
        #         name = project.name + ' : ' + project.partner_id.name
        #     else:
        #         name = project.name
        #     res.append((project.id, name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        context = context or self.pool['res.users'].context_get(cr, uid)
        project_selection = super(ProjectProject, self).name_search(cr, uid, name, args, operator, context=context,
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
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        sale_order_obj = self.pool['sale.order']
        for project in self.browse(cr, uid, ids, context):
            name = project.name.split('-')[0].replace(' ', '')
            result[project.id] = sale_order_obj.search(cr, uid, [('name', 'like', name)], context=context)

        return result

    def _get_purchase_order(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        sale_order_obj = self.pool['sale.order']
        purchase_order_line_obj = self.pool['purchase.order.line']

        order_requirement_obj = self.pool.get('order.requirement')  # in this mode test if exist order requirement

        for project in self.browse(cr, uid, ids, context):
            purchase_ids = []
            account_analytic_id = project.analytic_account_id.id
            purchase_sale_ids = []
            if order_requirement_obj:
                sale_order_ids = sale_order_obj.search(cr, uid, [('project_id', '=', account_analytic_id)], context=context)
                order_requirement_ids = order_requirement_obj.search(cr, uid, [('sale_order_id', 'in', sale_order_ids)], context=context)
                purchase_sale_ids = purchase_order_line_obj.search(cr, uid, [('order_requirement_ids', 'in', order_requirement_ids)], context=context)

            purchase_order_line_ids = purchase_order_line_obj.search(cr, uid, [('account_analytic_id', '=', account_analytic_id)], context=context)

            for purchase_order_line in purchase_order_line_obj.browse(cr, uid, list(set(purchase_order_line_ids + purchase_sale_ids)), context):
                purchase_ids.append(purchase_order_line.order_id.id)
            result[project.id] = list(set(purchase_ids))
            # name = project.name.split('-')[0]
            # result[project.id] = purchase_order_obj.search(cr, uid, [('origin', 'ilike', name), ('state', 'not in', ['draft', 'cancel'])], context=context)

        return result

    def _get_planned_end_date(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for project in self.browse(cr, uid, ids, context=context):
            time_list = []
            for task in project.tasks:
                if task.state == 'done':
                    time_list.append(task.date_end[:10])
                elif task.date_deadline:
                    time_list.append(task.date_deadline)
            res[project.id] = time_list and max(time_list) or False
        return res

    def _get_project(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for line in self.pool['project.task'].browse(cr, uid, ids, context=context):
            result[line.project_id.id] = True
        return result.keys()

    def _get_project_account(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        analytic_account_ids = []
        for line in self.pool['account.analytic.line'].browse(cr, uid, ids, context=context):
            if line.account_id:
                analytic_account_ids.append(line.account_id.id)
        for project_id in self.pool['project.project'].search(cr, uid, [('analytic_account_id', 'in', analytic_account_ids)],  context=context):
            result[project_id] = True
        return result.keys()

    # def _get_project_account_invoice(self, cr, uid, ids, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     print "_get_project_account_invoice"
    #     result = {}
    #     for line in self.pool['account.analytic.line'].browse(cr, uid, ids, context=context):
    #         if line.account_id:
    #             for project in self.pool['project.project'].search(cr, uid,
    #                                                                [('analytic_account_id', '=', line.account_id.id)],
    #                                                                context=context):
    #                 result[project] = True
    #     import pdb;pdb.set_trace()
    #     return result.keys()

    def _get_project_order_line(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for line in self.pool['sale.order.line'].browse(cr, uid, ids, context=context):
            if line.order_id.project_id and line.order_id.project_id.id:
                result[line.order_id.project_project.id] = True
        return result.keys()

    def _get_project_order(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for order in self.pool['sale.order'].browse(cr, uid, ids, context=context):
            if hasattr(order, 'project_project') and order.project_project:
                result[order.project_project.id] = True
        return result.keys()

    _columns = {
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True),
        'sale_order_ids': fields.function(_get_sale_order, 'Sale Order', type='one2many', relation="sale.order",
                                          readonly=True, method=True),
        'purchase_order_ids': fields.function(_get_purchase_order, 'Purchase Order', type='one2many',
                                              relation="purchase.order",
                                              readonly=True, method=True),
        'task_count': fields.function(_task_count, type='integer', string="Open Tasks", store={
            'project.project': (lambda self, cr, uid, ids, c={}: ids, ['tasks'], 50),
            'project.task': (_get_project, ['state', 'project_id'], 10),
        }, ),
        'planned_end_date': fields.function(_get_planned_end_date, type='date', string="Planned End Date", store={
            'project.project': (lambda self, cr, uid, ids, c={}: ids, ['tasks'], 50),
            'project.task': (_get_project, ['state', 'date_end', 'date_deadline', 'project_id'], 20),
        }, ),
        'project_task_work_ids': fields.one2many('project.task.work', 'project_id', 'Project Task Work'),

        # 'total_sell': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Sell Amount"),
        # 'total_sell_service': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Service Sell Amount"),
        # 'total_spent': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Spent Amount"),
        # 'total_service_spent': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Service Spent Amount"),
        # 'total_invoice': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'), multi='sums', string="Invoice Amount"),
        'total_sell': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'),
                                      multi='sums', string="Sell Amount", store={
                'sale.order': (_get_project_order, ['state'], 50),
                'sale.order.line': (_get_project_order_line, ['price_unit', 'price_subtotal'], 50),
            }, ),
        'total_sell_service': fields.function(_total_account, type='float',
                                              digits_compute=dp.get_precision('Sale Price'), multi='sums',
                                              string="Service Sell Amount", store={
                'sale.order': (_get_project_order, ['state'], 50),
                'sale.order.line': (_get_project_order_line, ['price_unit', 'price_subtotal'], 50),
            }, ),
        'total_spent': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'),
                                       multi='sums', string="Spent Amount", store={
                'account.analytic.line': (_get_project_account, ['amount', 'account_id'], 60),
            }, ),
        'total_service_spent': fields.function(_total_account, type='float',
                                               digits_compute=dp.get_precision('Sale Price'), multi='sums',
                                               string="Service Spent Amount", store={
                'account.analytic.line': (_get_project_account, ['amount', 'account_id'], 70),
            }, ),
        'total_invoice': fields.function(_total_account, type='float', digits_compute=dp.get_precision('Sale Price'),
                                         multi='sums', string="Invoice Amount", store={
                'account.analytic.line': (_get_project_account, ['amount', 'invoice_id', 'account_id'], 80),
            }, ),
        # 'doc_count': fields.function(
        #     _get_attached_docs, string="Number of documents attached", type='integer'
        # )
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        default.update({
            'project_task_work_ids': False,
        })
        res_id = super(ProjectProject, self).copy(cr, uid, ids, default, context)
        return res_id
