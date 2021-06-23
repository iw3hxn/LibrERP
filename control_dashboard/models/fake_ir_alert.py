# -*- coding: utf-8 -*-
##############################################################################
#
#    by Bortolatto Ivan (ivan.bortolatto at didotech.com)
#    Copyright (C) 2013 Didotech Inc. (<http://www.didotech.com>)
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
# from datetime import date
from datetime import timedelta

import pytz
from tools.translate import _

from openerp.osv import expression
from openerp.osv import orm, fields

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class FakeIrAlert(orm.Model):

    _name = "fake.ir.alert"
    _order = 'name'
    _columns = {
        'alert_id': fields.integer('Alert Id'),
        'name': fields.char('Name', size=256),
        'user_id': fields.many2one('res.users', 'User', required=True, readonly="True"),
        'type': fields.selection([
            ('warning', 'Warning'),
            ('activity', 'Activity TODO'),
        ], 'Type Alert', required=True),
        'link': fields.char('Object', size=256),
        'note': fields.text('Notes'),
        'mail_addresses': fields.char('Mail Addresses', size=256),
        'subject': fields.char('Subject', size=256),
        'email_message': fields.text('Email Message'),
        'state': fields.selection([
            ('open', 'Open'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ], 'State Alert', readonly=True),
    }

    def read(self, cr, uid, ids, fields_to_read=None, context=None, load='_classic_read'):
        my_records = super(FakeIrAlert, self).read(cr, uid, ids, ['name', 'alert_id', 'id'], context, load)
        if my_records not in ([], False, ''):
            list_not_deleted_ids = []
            for my_record in my_records:
                if my_record['alert_id'] in list_not_deleted_ids:
                    super(FakeIrAlert, self).unlink(cr, uid, my_record['id'], context=context)
                else:
                    list_not_deleted_ids = list_not_deleted_ids + [my_record['alert_id']]
        res = super(FakeIrAlert, self).read(cr, uid, ids, fields_to_read, context, load)
        return res

    def send_link(self, cr, uid, ids, context=None):
        alert_data = self.read(cr, uid, ids, context=context)
        return {'type': 'ir.actions.act_url', 'url': alert_data[0]['link'], 'target': 'new'}

    def button_send_mail(self, cr, uid, ids, context=None):
        obj_user = self.pool.get('res.users')
        obj_mail = self.pool.get('mail.compose.message')
        
        email_dict = {}
        my_data = obj_user.read(cr, uid, ids, context=context)
        email_dict['email_from'] = my_data['user_email']
        email_dict['email_to'] = context['mail_addresses']
        email_dict['subject'] = context['subject']
        email_dict['body_text'] = context['email_message']
        email_id = obj_mail.create(cr, uid, email_dict, context)
        obj_mail.send_mail(cr, uid, [email_id], context={'mail.compose.message.mode': ''})
        return True

