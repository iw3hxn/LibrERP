#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Didotech SRL
#
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
#

from openerp.osv import fields, osv
from openerp.tools import html2text
from datetime import *
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger('task')


class task_expired_config(osv.Model):

    """
    """
    _name = 'task.expired.config'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(task_expired_config, self).default_get(cr, uid, fields,
                                                           context=context)
        model_ids = self.search(cr, uid, [], context=context)
        if model_ids:
            return self.read(cr, uid, model_ids[0], [], context=context)
        return res

    _columns = {
        'without_change': fields.integer('Without Changes Days',
                                         help='Days number that tasks may '
                                         'have without changes.\n'
                                         'When these days finish an '
                                         'email information is sent'),
        'before_expiry': fields.integer('Before Expiry',
                                        help='Number days before to the '
                                        'expiry day to send an alert '
                                        'for email'),
        'without_change_tmpl_id': fields.many2one('email.template', 'Template Without Changes', domain="[('model_id', '=', 'project.task')]", required=True),
        'before_expiry_tmpl_id': fields.many2one('email.template', 'Template Without Changes', domain="[('model_id', '=', 'project.task')]", required=True)
    }

    def create_config(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        model_ids = self.search(cr, uid, [], context=context)
        dict_read = self.read(cr, uid, ids[0], [], context=context)
        if model_ids:
            self.write(cr, uid, model_ids, {
                'before_expiry': dict_read.get('before_expiry'),
                'without_change_tmpl': dict_read.get('without_change_tmpl_id')[0],
                'without_change': dict_read.get('without_change'),
                'before_expiry_tmpl_id': dict_read.get('before_expiry_tmpl_id')[0],
            }, context=context)

            return {'type': 'ir.actions.act_window_close'}

        return {'type': 'ir.actions.act_window_close'}

    def send_expiration_message(self, cr, uid, context=None):

        context = context or self.pool['res.users'].context_get(cr, uid)

        message_obj = self.pool['mail.message']
        task_obj = self.pool['project.task']
        work_obj = self.pool['project.task.work']
        config_ids = self.search(cr, uid, [], context=context)
        if config_ids:
            config_brw = self.browse(cr, uid, config_ids[0], context=context)
            today = date.today()
            before_expiry = today + timedelta(days=config_brw.before_expiry)
            last_change = today - timedelta(days=config_brw.without_change)
            today = today.strftime('%Y-%m-%d')
            before_expiry = before_expiry.strftime('%Y-%m-%d')
            last_change = last_change.strftime('%Y-%m-%d')
            task_ids = task_obj.search(cr, uid, [('state', 'not in', ('done', 'cancelled'))], context=context)
            for task in task_obj.browse(cr, uid, task_ids, context):
                no_change = False
                near_deadline = False
                last_message_ids = message_obj.search(cr, uid, [('res_id', '=', task.id), ('model', '=', 'project.task')], context=context, order='date desc')
                last_fecha = last_message_ids and message_obj.browse(cr, uid, last_message_ids[0]).date
                if work_obj.search(cr, uid, [('date', '<=', last_change), ('task_id', '=', task.id)], context=context) or last_fecha and last_fecha <= last_change:
                    no_change = True
                if task.date_deadline and task.date_deadline == before_expiry:
                    near_deadline = True
                if no_change:
                    self.pool['email.template'].send_mail(cr, uid, config_brw.without_change_tmpl_id.id, task.id, force_send=False, context=context)
                    _logger.info(u'Sent Email without change for {name} #{task_id}, email notification sent.'.format(name=self._name, task_id=task.id))
                if near_deadline:
                    self.pool['email.template'].send_mail(cr, uid, config_brw.before_expiry_tmpl_id.id, task.id, force_send=False, context=context)
                    _logger.info(u'Sent Email near deadline for {name} #{task_id}, email notification sent.'.format(name=self._name, task_id=task.id))

        return True
