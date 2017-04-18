# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Pexego Sistemas Informáticos (http://www.pexego.es) All Rights Reserved
#    $Jesús Ventosinos Mayor$
#    $Javier Colmenero Fernández$
#    Copyright (c) 2014 Didotech srl (info at didotech.com)
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

from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import orm, fields


class project_task(orm.Model):
    _inherit = "project.task"

    def _get_users_working(self, cr, uid, ids, field_name, args, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
            
        res = {}
        user_task_obj = self.pool["time.control.user.task"]
        
        for task in self.browse(cr, uid, ids, context):
            stream = ''
            user_ids = []
            user_task_ids = user_task_obj.search(cr, uid, [('started_task', '=', task.id)])
            if user_task_ids:
                for user_task in user_task_obj.browse(cr, uid, user_task_ids, context):
                    if user_task.user.name:
                        stream += user_task.user.name + u","
                    user_ids.append(user_task.user.id)
                    
                res[task.id] = {'working_users': stream, 'user_is_working': uid in user_ids}
            else:
                res[task.id] = {'working_users': '', 'user_is_working': False}
        return res
    
    _columns = {
        'other_users_ids': fields.many2many('res.users', 'project_task_user_rel', 'user_id', 'task_id', 'Other users'),
        'state': fields.selection([
            ('draft', 'New'),
            ('open', 'In Progress'),
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('working', 'Working'),
            ('cancelled', 'Cancelled')
        ], 'State', readonly=True, required=True),
        'working_users': fields.function(_get_users_working, method=True, string='Working users', type='char', size=255, multi=True),
        'user_is_working': fields.function(_get_users_working, method=True, string='I am working', type='boolean', multi=True)
    }

    def stop_task(self, cr, uid, task_id, final, user_task, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        
        self.pool['time.control.user.task'].write(cr, uid, user_task.id, {'work_end': final}, context)
        
        context['user_id'] = uid
        context['user_task_id'] = user_task.id
        # Call wizard:
        wizard_id = self.pool["task.time.control.confirm.wizard"].create(cr, uid, {
            'task_to_start': task_id,
            'user_task': user_task.id,
            'started_task': user_task.started_task.id
        }, context=context)
        
        return {
            'name': _("Confirm Time"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'task.time.control.confirm.wizard',
            'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }
      
    def work_start_btn(self, cr, uid, task_ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        start = datetime.now()
        user_task_obj = self.pool['time.control.user.task']
        project_task_obj = self.pool['project.task']
        
        user_task_ids = user_task_obj.search(cr, uid, [('user', '=', uid), ('started_task', 'in', task_ids)], context=context)
        
        if user_task_ids:
            user_task = user_task_obj.browse(cr, uid, user_task_ids, context)[0]
            if user_task.started_task:
                if user_task.started_task.id == task_ids[0]:
                    raise orm.except_orm(_("Warning !"), _("Task is alredy started."))
                return self.stop_task(cr, uid, task_ids[0], start, user_task, context)
            else:
                task = project_task_obj.browse(cr, uid, task_ids, context)[0]
                if task.state == 'draft':
                    self.do_open(cr, uid, task_ids, context)
                project_task_obj.write(cr, uid, task_ids, {'state': 'working'})
                user_task_obj.write(cr, uid, user_task_ids, {'work_start': start, 'started_task': task_ids[0]}, context)
        else:
            task = self.pool.get('project.task').browse(cr, uid, task_ids, context)[0]
            if task.state == 'draft':
                self.do_open(cr, uid, task_ids, context)
            
            user_task_obj.create(cr, uid, {
                'user': uid,
                'work_start': start,
                'started_task': task_ids[0]
            }, context)
            project_task_obj.write(cr, uid, task_ids, {'state': 'working'}, context)
        return True
        
    def work_end_btn(self, cr, uid, task_ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        end_datetime = datetime.now()
        user_task_obj = self.pool['time.control.user.task']
        
        user_task_ids = user_task_obj.search(cr, uid, [('user', '=', uid), ('started_task', 'in', task_ids)], context=context)
        if user_task_ids:
            user_task = user_task_obj.browse(cr, uid, user_task_ids[0], context)
            if user_task.started_task.id == task_ids[0]:
                finished = self.stop_task(cr, uid, None, end_datetime, user_task, context)
                if finished:
                    return finished
                else:
                    raise orm.except_orm(_("Warning!"), _('Task is not init.'))
            else:
                raise orm.except_orm(_("Warning!"), _('Task started by another user.'))
        else:
            raise orm.except_orm(_("Warning!"), _('User has no opened tasks.'))
        return True


