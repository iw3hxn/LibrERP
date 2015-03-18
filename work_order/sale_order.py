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
        
        orders = self.browse(cr, uid, ids)
        for order in orders:
            if order.project_id:
                project_ids = project_obj.search(cr, uid, [('analytic_account_id', '=', order.project_id.id)])
                if project_ids:
                    project = project_obj.browse(cr, uid, project_ids[0])
                    result[order.id] = (project.id, project.name)
                else:
                    result[order.id] = False
            else:
                result[order.id] = False

        return result
    
    def _write_project(self, cr, uid, ids, field_name, field_value, arg, context):
        if not field_value:
            return False
        
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        
        project = self.pool['project.project'].browse(cr, uid, field_value)
        
        orders = self.browse(cr, uid, ids)
        for order in orders:
            # Yes, it's crazy. Thanks to the authors of the sale_order for the wrong field name
            self.write(cr, uid, order.id, {'project_id': project.analytic_account_id.id})
        return True
         
    _columns = {
        'project_project': fields.function(_read_project, obj='project.project', fnct_inv=_write_project, string=_('Project'), method=True, type='many2one'),
    }

    def action_cancel(self, cr, uid, ids, context=None):
        result = super(sale_order, self).action_cancel(cr, uid, ids, context)
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            if order.project_project:
                project_obj = self.pool['project.project']
                task_obj = self.pool['project.task']
                analytic_account_obj = self.pool['account.analytic.account']
                analytic_account_line_obj = self.pool['account.analytic.line']
                unlink_project = True
                for task in order.project_project.tasks:
                    if not task.work_ids:
                        task_obj.unlink(cr, uid, [task.id], context=context)
                    else:
                        task_obj.action_close(cr, uid, [task.id], context=context)
                        unlink_project = False

                analytic_account_line_ids = analytic_account_line_obj.search(cr, uid, [('account_id', '=', order.project_project.analytic_account_id.id)])
                sale_order_ids = self.search(cr, uid, [('project_project', '=', order.project_project.id)])
                if unlink_project and not analytic_account_line_ids and len(sale_order_ids) > 1:
                    analytic_account_id = order.project_project.analytic_account_id.id
                    project_obj.unlink(cr, uid, [order.project_project.id], context=context)
                    analytic_account_obj.unlink(cr, uid, [analytic_account_id], context=context)
                else:
                    project_obj.set_done(cr, uid, [order.project_project.id], context=context)

        return result

    def action_cancel_draft(self, cr, uid, ids, context=None):
        result = super(sale_order, self).action_cancel_draft(cr, uid, ids, context)
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            shop = self.pool['sale.shop'].browse(cr, uid, [order.shop_id.id], context=context)[0]
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
                self.write(cr, uid, [order.id], {'project_project': project_id}, context=context)
        return result

    def action_wait(self, cr, uid, ids, context=None):
        result = super(sale_order, self).action_wait(cr, uid, ids, context)
        
        bom_obj = self.pool['mrp.bom']
        sale_line_bom_obj = self.pool.get('sale.order.line.mrp.bom') or False
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            if order.project_project and order.company_id.create_task:
                project_id = order.project_project.id
                if order.order_policy == 'picking':
                    invoice_ratio = 1
                else:
                    invoice_ratio = 3
                self.pool['project.project'].write(cr, uid, project_id, {'to_invoice' : invoice_ratio, 'state' : 'open'})
                for order_line in order.order_line:
                    task_vals = False
                    if order_line.product_id and order_line.product_id.is_kit:
                        # test id module sale_bom is installad
                        if sale_line_bom_obj:
                            service_boms = [sale_line_bom for sale_line_bom in order_line.mrp_bom if (sale_line_bom.product_id.type == 'service' and sale_line_bom.product_id.purchase_ok == False)]
                            for bom in service_boms:
                                if bom.product_id.uom_id.id == user.company_id.hour.id:
                                    planned_hours = bom.product_uom_qty
                                else:
                                    planned_hours = 0
                                task_vals = {
                                    'name': u"{0}: {1} - {2}".format(order.project_project.name, order_line.product_id.name, bom.product_id.name),
                                    'project_id': project_id,
                                    'planned_hours': planned_hours,
                                    'remaining_hours': planned_hours,
                                    'origin': 'sale.order.line, {0}'.format(order_line.id)
                                }
                        else:
                            main_bom_ids = bom_obj.search(cr, uid, [('product_id', '=', order_line.product_id.id), ('bom_id', '=', False)], context=context)
                            if main_bom_ids:
                                if len(main_bom_ids) > 1:
                                    _logger.warning(_(u"More than one BoM defined for the '{0}' product!").format(order_line.product_id.name))
                                
                                bom_ids = bom_obj.search(cr, uid, [('bom_id', '=', main_bom_ids[0])], context=context)
                                boms = bom_obj.browse(cr, uid, bom_ids, context=context)
                                service_boms = [bom for bom in boms if (bom.product_id.type == 'service' and order_line.product_id.purchase_ok == False)]
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
                                        'origin': 'sale.order.line, {0}'.format(order_line.id)
                                    }
                            
                    elif order_line.product_id and order_line.product_id.type == 'service' and order_line.product_id.purchase_ok == False:
                        if order_line.product_id.uom_id.id == user.company_id.hour.id:
                            planned_hours = order_line.product_uom_qty
                        else:
                            planned_hours = 0
                        task_vals = {
                            'name': u"{0}: {1}".format(order.name, order_line.product_id.name),
                            'project_id': project_id,
                            'planned_hours': planned_hours,
                            'remaining_hours': planned_hours,
                            'origin': 'sale.order.line, {0}'.format(order_line.id)
                        }
                    if task_vals:
                        if order.company_id.task_no_user:
                            task_vals['user_id'] = False
                        self.pool['project.task'].create(cr, uid, task_vals, context=context)
        return result

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'project_project': False,
                        'project_id': False, })
        return super(sale_order, self).copy(cr, uid, id, default, context)

    def create(self, cr, uid, values, context=None):
        order_id = super(sale_order, self).create(cr, uid, values, context)
        order = self.browse(cr, uid, order_id, context=context)
        shop = self.pool['sale.shop'].browse(cr, uid, values['shop_id'], context=context)
        if order.order_policy == 'picking':
            invoice_ratio = 1
        else:
            invoice_ratio = 3
        if (not values.get('project_project', False)) and (not values.get('project_id', False)) and shop and shop.project_required and (not order.project_project or not context.get('versioning', False)):
            value = {
                'name': values['name'],
                'partner_id': values.get('partner_id', False),
                'to_invoice' : invoice_ratio,
                'state' : 'pending',
            }
            # i use this mode because if there are no project_id on shop use default value
            if shop.project_id:
                value['parent_id'] = shop.project_id.id
            
            project_id = self.pool['project.project'].create(cr, uid, value, context={
                'model': 'sale.order',
            })
            
            self.write(cr, uid, order_id, {'project_project': project_id}, context=context)
        
        return order_id


class sale_shop(orm.Model):
    _inherit = 'sale.shop'
    
    _columns = {
        'project_required': fields.boolean(_('Require a Project')),
    }
    
    _defaults = {
        'project_required': True
    }
