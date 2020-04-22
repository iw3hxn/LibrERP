# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
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
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class sale_order(orm.Model):
    _inherit = 'sale.order'
    
    def _read_project(self, cr, uid, ids, field_name, args, context):
        result = {}
        project_obj = self.pool['project.project']

        for order in self.read(cr, uid, ids, ['project_id'], context):
            result[order['id']] = False
            if order['project_id']:
                project_ids = project_obj.search(cr, uid, [('analytic_account_id', '=', order['project_id'][0])], context=context)
                if project_ids:
                    result[order['id']] = project_obj.name_get(cr, uid, project_ids, context)[0]

        return result
    
    def _write_project(self, cr, uid, ids, field_name, field_value, arg, context):
        if not field_value:
            return False
        
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        
        project = self.pool['project.project'].browse(cr, uid, field_value, context)
        self.write(cr, uid, ids, {'project_id': project.analytic_account_id.id}, context)

        # for order in self.browse(cr, uid, ids, context):
        #     # Yes, it's crazy. Thanks to the authors of the sale_order for the wrong field name
        #     self.write(cr, uid, order.id, {'project_id': project.analytic_account_id.id})
        return True

    def _get_project_task(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        project_task_obj = self.pool['project.task']
        sale_order_obj = self.pool['sale.order']

        for order in sale_order_obj.browse(cr, uid, ids, context):
            result[order.id] = project_task_obj.search(cr, uid, [('project_id', '=', order.project_project.id)], context=context)
        return result
         
    _columns = {
        'project_project': fields.function(_read_project, obj='project.project', fnct_inv=_write_project, string=_('Project'), method=True, type='many2one'),
        'project_task_ids': fields.function(_get_project_task, 'Project Task', type='one2many', relation="project.task", readonly=True, method=True),
    }

    def action_cancel(self, cr, uid, ids, context=None):
        result = super(sale_order, self).action_cancel(cr, uid, ids, context)
        for order in self.browse(cr, uid, ids, context=context):
            if order.project_project:
                project_obj = self.pool['project.project']
                task_obj = self.pool['project.task']
                analytic_account_line_obj = self.pool['account.analytic.line']
                unlink_project = True
                for task in order.project_project.tasks:
                    if not task.work_ids:
                        task_obj.unlink(cr, uid, [task.id], context=context)
                    else:
                        task_obj.action_close(cr, uid, [task.id], context=context)
                        unlink_project = False

                analytic_account_line_ids = analytic_account_line_obj.search(cr, uid, [('account_id', '=', order.project_project.analytic_account_id.id)], context=context)
                sale_order_ids = self.search(cr, uid, [('project_project', '=', order.project_project.id)], context=context)
                if unlink_project and not analytic_account_line_ids and len(sale_order_ids) > 1:
                    project_obj.unlink(cr, uid, [order.project_project.id], context=context)
                else:
                    project_obj.set_done(cr, uid, [order.project_project.id], context=context)

        return result

    def action_cancel_draft(self, cr, uid, ids, context=None):
        result = super(sale_order, self).action_cancel_draft(cr, uid, ids, context)
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            shop = order.shop_id
            if (not order.project_project) and (not order.project_id) and shop and shop.project_required and (not order.project_project or not context.get('versioning', False)):
                if order.order_policy == 'picking':
                    invoice_ratio = 1
                else:
                    invoice_ratio = 3
                value = {
                    'name': order.name,
                    'partner_id': order.partner_id and order.partner_id.id or False,
                    'to_invoice': invoice_ratio,
                    'state': 'pending',
                }
                # i use this mode because if there are no project_id on shop use default value
                if shop.project_id:
                    value['parent_id'] = shop.project_id.id

                project_id = self.pool['project.project'].create(cr, uid, value, context={
                    'model': 'sale.order',
                })
                order.write({'project_project': project_id})

        return result

    def create_task(self, cr, uid, order_line, task_number, task_vals, context):
        for matrix_line in order_line.order_id.company_id.sale_task_matix_ids:

            if matrix_line.sale_order_field_id:
                lst = self.pool['sale.order'].read(cr, uid, order_line.order_id.id, [matrix_line.sale_order_field_id.name], context)[matrix_line.sale_order_field_id.name]
                if isinstance(lst, (list, tuple)):
                    lst = lst[0]
                task_vals[matrix_line.task_field_id.name] = lst

            if matrix_line.sale_order_line_field_id:
                lst = self.pool['sale.order.line'].read(cr, uid, order_line.id, [matrix_line.sale_order_line_field_id.name], context)[matrix_line.sale_order_line_field_id.name]
                if isinstance(lst, (list, tuple)):
                    lst = lst[0]
                task_vals[matrix_line.task_field_id.name] = lst

        if order_line.order_id.company_id.task_no_user and not context.get('force_user', False):
            task_vals['user_id'] = False

        for task in range(task_number):
            self.pool['project.task'].create(cr, uid, task_vals, context=context)

        return True

    def _change_project_name(self, cr, uid, ids, order, context):
        project_name = order.name.split(' ')[0]
        if order.client_order_ref:
            project_name = project_name + ' - ' + order.client_order_ref
        return project_name

    def action_wait(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid, context)
        result = super(sale_order, self).action_wait(cr, uid, ids, context)
        bom_obj = self.pool['mrp.bom']
        sale_line_bom_obj = self.pool.get('sale.order.line.mrp.bom')  # WARNING: in this mode test if exist object 'sale.order.line.mrp.bom'
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)

        for order in self.browse(cr, uid, ids, context=context):
            sequence = 10
            if order.project_project and order.company_id.create_task:
                project_id = order.project_project.id
                if order.order_policy == 'picking':
                    invoice_ratio = 1
                else:
                    invoice_ratio = 3
                project_name = self._change_project_name(cr, uid, ids, order, context)

                self.pool['project.project'].write(cr, uid, project_id, {'to_invoice': invoice_ratio, 'state': 'open', 'name': project_name}, context=context)
                for order_line in order.order_line:
                    task_number = 1
                    if order_line.product_id and order_line.product_id.is_kit:
                        # test if module sale_bom is installad
                        if sale_line_bom_obj:
                            product_boms = list(set([sale_line_bom.parent_id and sale_line_bom.parent_id for sale_line_bom in order_line.mrp_bom if (sale_line_bom.parent_id.type == 'service' and sale_line_bom.parent_id.supply_method == 'produce')]))
                            if product_boms:
                                for product in product_boms:
                                    task_vals = {
                                        'name': u"{0}: {1} - {2}".format(order.project_project.name,
                                                                         order_line.product_id.name,
                                                                         product.name),
                                        'project_id': project_id,
                                        'partner_id': order.partner_id.id,
                                        'planned_hours': 1, #int(planned_hours / task_number),
                                        'remaining_hours': 1, #int(planned_hours / task_number),
                                        'origin': 'sale.order.line, {0}'.format(order_line.id),
                                        'sequence': sequence,
                                    }
                                    sequence += 10
                                    self.create_task(cr, uid, order_line, task_number, task_vals, context)
                            else:
                                service_boms = [sale_line_bom for sale_line_bom in order_line.mrp_bom if (sale_line_bom.product_id.type == 'service' and not sale_line_bom.product_id.purchase_ok)]
                                for bom in service_boms:
                                    if bom.product_uom.id == user.company_id.hour.id:
                                        planned_hours = bom.product_uom_qty
                                    else:
                                        planned_hours = self.pool['product.uom']._compute_qty(cr, uid, bom.product_uom.id, bom.product_uom_qty, bom.product_id.uom_id.id)
                                        task_number = int(bom.product_uom_qty)
                                    if task_number:
                                        task_vals = {
                                            'name': u"{0}: {1}".format(bom.product_id.name, order_line.product_id.name),
                                            'project_id': project_id,
                                            'partner_id': order.partner_id.id,
                                            'planned_hours': int(planned_hours / task_number),
                                            'remaining_hours': int(planned_hours / task_number),
                                            'origin': 'sale.order.line, {0}'.format(order_line.id),
                                            'sequence': sequence,
                                        }
                                        sequence += 10
                                        self.create_task(cr, uid, order_line, task_number, task_vals, context)

                        else:
                            main_bom_ids = bom_obj.search(cr, uid, [('product_id', '=', order_line.product_id.id), ('bom_id', '=', False)], context=context)
                            if main_bom_ids:
                                if len(main_bom_ids) > 1:
                                    _logger.warning(_(u"More than one BoM defined for the '{0}' product!").format(order_line.product_id.name))
                                
                                bom_ids = bom_obj.search(cr, uid, [('bom_id', '=', main_bom_ids[0])], context=context)
                                boms = bom_obj.browse(cr, uid, bom_ids, context=context)
                                service_boms = [bom for bom in boms if (bom.product_id.type == 'service' and not order_line.product_id.purchase_ok)]
                                for bom in service_boms:
                                    if bom.product_uom.id == user.company_id.hour.id:
                                        planned_hours = bom.product_qty
                                    else:
                                        planned_hours = 0
                                    task_vals = {
                                        'name': u"{0}: {1}".format(order.project_project.name, bom.product_id.name),
                                        'project_id': project_id,
                                        'planned_hours': planned_hours,
                                        'remaining_hours': planned_hours,
                                        'origin': 'sale.order.line, {0}'.format(order_line.id),
                                        'sequence': sequence,
                                    }
                                    sequence += 10
                                    self.create_task(cr, uid, order_line, task_number, task_vals, context)
                            
                    elif order_line.product_id and order_line.product_id.type == 'service' and not order_line.product_id.purchase_ok:
                        if order_line.product_id.uom_id.id == user.company_id.hour.id:
                            planned_hours = order_line.product_uom_qty
                        else:
                            planned_hours = 0

                        if order_line.product_id.name_get()[0][1] == order_line.name:
                            task_name = order_line.product_id.name
                        else:
                            task_name = order_line.name

                        task_vals = {
                            'name': u"{0}: {1}".format(order.name, task_name),
                            'project_id': project_id,
                            'planned_hours': planned_hours,
                            'remaining_hours': planned_hours,
                            'origin': 'sale.order.line, {0}'.format(order_line.id),
                            'sequence': sequence,
                        }
                        sequence += 10
                        self.create_task(cr, uid, order_line, task_number, task_vals, context)

        return result

    def copy(self, cr, uid, id, default=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if default is None:
            default = {}
        if not context.get('versioning', False):
            default.update({
                'project_project': False,
                'project_id': False,
            })
        return super(sale_order, self).copy(cr, uid, id, default, context)

    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order, self).write(cr, uid, ids, vals, context)
        if 'partner_id' in vals:
            analytic_account_ids = []
            orders_project = self.read(cr, uid, ids, ['project_id'], context)
            for order in orders_project:
                if order['project_id']:
                    analytic_account_ids.append(order['project_id'][0])
            if analytic_account_ids:
                analytic_account_vals = {
                    'partner_id': vals['partner_id']
                }
                if vals.get('partner_order_id', False):
                    analytic_account_vals.update({
                        'contact_id': vals['partner_order_id']
                    })
                self.pool['account.analytic.account'].write(cr, uid, list(set(analytic_account_ids)), analytic_account_vals, context)
        return res

    def create(self, cr, uid, values, context=None):
        order_id = super(sale_order, self).create(cr, uid, values, context)
        order = self.browse(cr, uid, order_id, context=context)
        shop = self.pool['sale.shop'].browse(cr, uid, values['shop_id'], context=context)
        if order.order_policy == 'picking':
            invoice_ratio = 1
        else:
            invoice_ratio = 3

        if (not values.get('project_project', False)) and (not values.get('project_id', False)) and shop and shop.project_required and (not order.project_project or not context.get('versioning', False)):
            project_values = {
                'name': values['name'].split(' ')[0],
                'partner_id': values.get('partner_id', False),
                'contact_id': values.get('partner_order_id', False),
                'pricelist_id': values.get('pricelist_id', False),
                'to_invoice': invoice_ratio,
                'state': 'pending',
                'warn_manager': True,
                'user_id': shop.project_manager_id and shop.project_manager_id.id or order.user_id and order.user_id.id or False,
            }

            if shop.member_ids:
                project_values['members'] = [(6, 0, [user.id for user in shop.member_ids])]

            if order.company_id.work_order_default_task_ids:
                task_values = []
                for task_template in order.company_id.work_order_default_task_ids:
                    task_values.append([0, 0, {
                        'name': task_template.name,
                        'planned_hours': task_template.planned_hours,
                        'user_id': task_template.user_id and task_template.user_id.id or False
                    }])
                project_values['tasks'] = task_values

            # todo think better with matrix / function project_manager
            # if values.get('section_id', False):
            #     sale_team = self.pool['crm.case.section'].browse(cr, uid, values['section_id'], context=context)
            #     if sale_team.user_id:
            #         project_values['user_id'] = sale_team.user_id.id

            # i use this mode because if there are no project_id on shop use default value
            if shop.project_id:
                project_values['parent_id'] = shop.project_id.id
            project_id = self.pool['project.project'].create(cr, uid, project_values, context=context.update({
                'model': 'sale.order',
            }))
            
            self.write(cr, uid, order_id, {'project_project': project_id}, context=context)
        
        return order_id


