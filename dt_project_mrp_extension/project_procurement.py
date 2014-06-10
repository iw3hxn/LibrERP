# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com) 
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields, osv, orm
import tools

class procurement_order(osv.osv):
    _inherit = "procurement.order"
    _columns = {
        'project_id': fields.many2one('project.project', 'Project'),
        'sale_line_ids': fields.one2many('sale.order.line','procurement_id','Sales Order Lines'),
        # 'sale_id': fields.many2one('sale.order', 'Sale Order', readonly=True),
        'sale_id':fields.related('sale_line_ids', 'order_id', type='many2one', relation='sale.order', string='Sale Order', store=True, readonly=True),
    }

    def _project_already_created(self,cr,uid,procurement):
        """ Return the ID of the project related to the SO 
            if it has already been created, otherwise False.
        """
        so_obj = self.pool.get('sale.order')
        proc_obj = self.pool.get('procurement.order')
        project_created_id = False
        
        proc_ids = so_obj.procurement_lines_get(cr,uid,[procurement.sale_id.id])
        
        for proc in proc_obj.browse(cr,uid,proc_ids):
            if proc.project_id:
                project_created_id = proc.project_id.id
                break
        return project_created_id
        
    def action_produce_assign_service(self, cr, uid, ids, context=None):
        """This will create the right object depending on the case:
           * By default create a new project cause no analytic account was set on Sale Order
             This project will be built with all SO line with a product of type service and
             the procurement will be linked to it.
           * If an analytic account has been set on product of a SO line, create a new task 
             related to concerned project and linked the procurement to it.
           * If an analytic account has been set on Sale order, create a new task related to 
             concerned the account and linked the procurement to it. """
           
        project_obj = self.pool.get('project.project')
        for procurement in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [procurement.id], {'state': 'running'})
            planned_hours = procurement.product_qty
            project_id = False
            # True if need to create project or if already done
            create_proj_or_already_done = True
            if procurement.product_id.project_id:
                project_id = procurement.product_id.project_id.id
                create_proj_or_already_done = False
            elif procurement.sale_id.project_id and not project_id:
                project_id = project_obj.search(cr,uid,[('analytic_account_id','=',procurement.sale_id.project_id.id)])[0]
                create_proj_or_already_done = False
            # Check if already created for this SO
            elif self._project_already_created(cr,uid,procurement) and create_proj_or_already_done:
                project_id = self._project_already_created(cr,uid,procurement)
            else:
                project_id = self.pool.get('project.project').create(cr, uid, {
                    'name': '%s:%s' % (procurement.origin or '', procurement.sale_id.client_order_ref or ''),
                    'date': procurement.date_planned,
                    # 'planned_hours':planned_hours,
                    # 'remaining_hours': planned_hours,
                    'user_id': procurement.product_id.product_manager.id,
                    'description': procurement.note,
                    'procurement_id': procurement.id,
                    # 'date_deadline': procurement.date_planned,
                    # 'project_id': project_id,
                    'state': 'open',
                    'company_id': procurement.company_id.id,
                },context=context)
            task_id = self.pool.get('project.task').create(cr, uid, {
                'name': '%s:%s' % (procurement.origin or '', procurement.name),
                'date_deadline': procurement.date_planned,
                'planned_hours':planned_hours,
                'remaining_hours': planned_hours,
                'user_id': procurement.product_id.product_manager.id,
                'notes': procurement.note,
                'procurement_id': procurement.id,
                'description': procurement.note,
                'date_deadline': procurement.date_planned,
                'project_id': project_id,
                'state': 'draft',
                'company_id': procurement.company_id.id,
            },context=context)
            # If no project created ever for this SO, then we associate the procurement to
            # tasks, otherwise, procurement is based on project
            if not create_proj_or_already_done:
                self.write(cr, uid, [procurement.id],{'task_id':task_id})
            else:
                self.write(cr, uid, [procurement.id],{'project_id':project_id})

        return task_id

procurement_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
