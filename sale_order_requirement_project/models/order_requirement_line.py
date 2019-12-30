# -*- coding: utf-8 -*-
# © 2019 Didotech srl (www.didotech.com)

import re

from openerp.osv import orm, fields


class OrderRequirementLine(orm.Model):

    _inherit = 'order.requirement.line'

    def _product_type_small(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.product_id.type == 'service':
                product_type = "S"
            elif line.product_id.is_kit:
                product_type = "K"
            else:
                product_type = "P"
            res[line.id] = product_type

        return res

    @staticmethod
    def get_task_state(ordreqline):
        # First -> all non null purchase order lines

        tasks = ordreqline.project_task_ids
        # Flat list -> all moves excluding canceled ones
        real_tasks = [task for task in tasks if task.state != 'cancel']
        tot = len(real_tasks)
        done = len([m for m in real_tasks if m.state == 'done'])
        return done, tot

    def _get_task_orders_state(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}

        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'project_task_state': '',
            }

            done, tot = self.get_task_state(line)
            task_orders_state = ''
            if tot > 0:
                task_orders_state = '%d/%d' % (done, tot)

            res[line.id] = {
                'project_task_state': task_orders_state,
            }

        return res

    _columns = {
        'product_type_small': fields.function(_product_type_small, type='char', string=" ", store=True),
        'project_task_ids': fields.many2many('project.task', string='Task'),
        'project_task_state': fields.function(_get_task_orders_state, method=True, type='char', size=16, multi='order_state', string='Tasks State', readonly=True),
        'description': fields.text('Task Note'),
        'planned_hours': fields.float('Planned Hours'),
        'connected_task_id': fields.many2one('order.requirement.line', string='Connected Order Task'),
        'product_order_requirement_id': fields.many2one('order.requirement.line', string='Hide reference field'),
        'connected_product_ids': fields.one2many('order.requirement.line', 'product_order_requirement_id', string='Product Used for task'),
    }

    def confirm_suppliers(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for line in self.browse(cr, uid, ids, context):
            if line.product_id.type == 'service' and not line.buy:
                project_task_obj = self.pool['project.task']
                self.write(cr, uid, line.id, {'state': 'done'}, context)
                project_task_vals = {}
                description = []
                for connect_product in line.connected_product_ids:
                    description.append(connect_product.name_get()[0][1])

                if line.sale_order_line_id.notes:
                    description.append(line.sale_order_line_id.notes)
                if description:
                    project_task_vals.update({
                        'description': '\n'.join(description)
                    })

                if line.sale_order_id.project_project and not line.connected_task_id:
                    project_task_vals.update({
                        'project_id': line.sale_order_id.project_project.id,
                        'name': re.compile('\[.*\]\ ').sub('', line.sale_order_line_id.name),
                        'user_id': line.user_id and line.user_id.id,
                        'order_requirement_line_ids': [(4, line.id)],
                        'planned_hours': line.planned_hours,
                        'partner_id': line.sale_order_id.partner_id.id
                    })

                    project_task_obj.create(cr, uid, project_task_vals, context)
                if line.connected_task_id:
                    connected_task_ids = project_task_obj.search(cr, uid, [('order_requirement_line_ids', 'in', line.id)], context=context)

            else:
                super(OrderRequirementLine, self).confirm_suppliers(cr, uid, [line.id], context)

        return {
            'type': 'ir.actions.act_window_close'
        }
    

