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

from openerp.osv import orm, fields, expression
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class ir_alert(orm.Model):

    _name = "ir.alert"
    _order = 'name'
    _columns = {
        'name': fields.char('To Do', size=256, required=True),
        'user_id': fields.many2one('res.users', 'User', required=True, readonly="True"),
        'user_ids': fields.many2many('res.users', 'inv_user_rel', 'invite_id', 'user_id', 'Users'),
        'model_id': fields.many2one('ir.model', 'Object', required=True, help="Select the object on which the action will work (read, write, create)."),
        'ids': fields.integer('Ids'),
        'is_child': fields.boolean('Is Child?'),
        'type': fields.selection([
            ('warning', 'Warning'),
            ('activity', 'Activity TODO'),
        ], 'Type Alert', required=True, states={'pending': [('readonly', True)]}),
        'state': fields.selection([
            ('open', 'Open'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ], 'State Alert', readonly=True),
        'link': fields.char('Object', size=256),
        'create_date': fields.datetime('Creation Date', readonly=True, select=True, help="Date on which Alert is created."),
        'complete_date': fields.datetime('Complete Date', readonly=True, select=True, help="Date on which Alert is created."),
        'note': fields.text('Notes'),
        'mail_addresses': fields.char('Mail Addresses', size=256),
        'subject': fields.char('Subject', size=256),
        'email_message': fields.text('Email Message'),
        'alert_config_id': fields.many2one('ir.alert.config', 'Alert Name', required=True),
    }
    _defaults = {
        'state': 'open',
        'type': 'warning',
        'user_id': lambda self, cr, uid, context: uid,
    }

    def unlink(self, cr, uid, ids, context=None):
        res = super(ir_alert, self).unlink(cr, uid, ids, context=context)
        return res
   
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})

    def prewiew_link(self, cr, uid, ids, context=None):
        ir_model_model = self.pool['ir.model']

        if isinstance(ids, list):
            if len(ids) > 1:
                raise orm.except_orm(
                    'Error',
                    'Can manage only one record')
            ids = ids[0]
        alert_data_link = self.read(cr, uid, ids, ['link'], context=context)['link']

        ref_obj, ref_id = alert_data_link.split(',')
        ref_id = long(ref_id)
        ref_obj_ids = ir_model_model.search(cr, uid, [('model', '=', ref_obj)], context=context, limit=1)
        if not ref_obj_ids:
            raise orm.except_orm(
                'Error',
                'Missing Model {}'.format(ref_obj))
        name = ir_model_model.read(cr, uid, ref_obj_ids, ['name'], context=context)[0]['name']
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'res_model': ref_obj,
            'view_type': 'form',
            'view_mode': 'page,form',
            'target': 'current',
            'res_id': ref_id,
        }

    def send_link(self, cr, uid, ids, context=None):
        res = self.prewiew_link(cr, uid, ids, context)
        self.write(cr, 1, ids, {'state': 'done'}, context)
        return res

    def button_send_mail(self, cr, uid, ids, context=None):
        obj_user = self.pool['res.users']
        obj_mail = self.pool['mail.compose.message']

        email_dict = {}
        if 'uid' in context:
            my_data = obj_user.read(cr, uid, context['uid'], context=context)

        if ('user_email' in my_data) and (my_data['user_email']):
            email_dict['email_from'] = my_data['user_email']
        else:
            raise orm.except_orm(_('Error'),
                                 _("Your E-Mail (message Sender), not valid. Valorize your exactly E-Mail address, please."))
            return False
        email_dict['email_to'] = context['mail_addresses']
        email_dict['subject'] = context['subject']
        email_dict['body_text'] = context['email_message']
        email_id = obj_mail.create(cr, uid, email_dict, context)

        obj_mail.send_mail(cr, uid, [email_id], context={'mail.compose.message.mode': ''})
        return True

    # create and management of message (cron's routine)
    def manage_alerts(self, cr, uid, context=None):
        # control change model' state
        self.control_state_message(cr, uid, context)

        alert_config_model = self.pool['ir.alert.config']
        ir_alert_model = self.pool['ir.alert']
        ir_model_model = self.pool['ir.model']
        ir_model_fields_model = self.pool['ir.model.fields']
        res_users_model = self.pool['res.users']
        obj_config_parameter = self.pool['ir.config_parameter']

        # my server and port
        host_ids = obj_config_parameter.search(cr, uid, [('key', '=', 'web.base.url')])
        host_data = obj_config_parameter.read(cr, uid, host_ids[0], context=context)

        # object's data
        obj_alert_ids = alert_config_model.search(cr, uid, [], context=context)

        # generate message
        for config_alert_data in alert_config_model.read(cr, uid, obj_alert_ids, context=context):
            obj_model_data = ir_model_model.read(cr, uid, config_alert_data['model_id'][0], context=context)
            if config_alert_data['date_comparison_field_id'] or config_alert_data['state_comparison']:
                search_domain = config_alert_data['domain']
                if config_alert_data['date_comparison_field_id']:
                    obj_fields_data = ir_model_fields_model.read(cr, uid, config_alert_data['date_comparison_field_id'][0],
                                                      context=context)

                    # correct date
                    access_user_data = res_users_model.read(cr, uid, uid, ['context_tz'], context=context)
                    if 'context_tz' in access_user_data:
                        if access_user_data['context_tz']:
                            local_timezone = pytz.timezone(access_user_data['context_tz'])
                        else:
                            local_timezone = pytz.timezone('UTC')
                    else:
                        local_timezone = pytz.timezone('UTC')
                    utc_timezone = pytz.timezone('UTC')
                    datetime_offset = utc_timezone.localize(
                        datetime.now() - timedelta(hours=config_alert_data['offset']))
                    datetime_offset = datetime_offset.astimezone(local_timezone)
                    date_offset = datetime_offset.date()
                    name_field_date = obj_fields_data['name']
                    if obj_fields_data['ttype'] == 'date':
                        date_offset_str = date_offset.strftime(DEFAULT_SERVER_DATE_FORMAT)
                        search_domain.append((name_field_date, '<=', date_offset_str))
                    else:
                        start_period = datetime_offset.replace(hour=0, minute=0, second=0, microsecond=0)
                        start_period_str = start_period.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        end_period = datetime_offset.replace(hour=23, minute=59, second=59, microsecond=0)
                        end_period_str = end_period.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        search_domain.append((name_field_date, '<=', end_period_str))
                        # condition += [(name_field_date, '>=', start_period_str), (name_field_date, '<=', end_period_str)]

                if config_alert_data['state_comparison']:
                    state_comparison = str(config_alert_data['state_comparison'])
                    search_domain.append(('state', '!=' if config_alert_data['flag_not_state'] else '=', state_comparison))

                # [('date_action', '<=', '2021-07-01'), ('state', '!=', 'done')]
                target_model = self.pool[obj_model_data['model']]
                target_model_ids = target_model.search(cr, uid, search_domain, context=context)
                # ids_existing_record = obj_alert.search(cr, uid, [('alert_config_id', '=', config_alert_data['id']), ('state', '=', 'open')], context=context)

                # existing message?
                user_field_id = False
                if config_alert_data['user_field_id']:
                    obj_fields_data = ir_model_fields_model.read(cr, uid, config_alert_data['user_field_id'][0],
                                                                 context=context)
                    user_field_id = obj_fields_data['name']

                for target_id in target_model_ids:
                    existing_message = self.search(cr, uid, [('model_id', '=', config_alert_data['model_id'][0]),
                                                             ('ids', '=', target_id), ('state', '=', 'open')], context=context)
                    if not existing_message:  # not exists: create message
                        message_dict = {}
                        # read object
                        row = target_model.browse(cr, uid, target_id, context=context)
                        # compose name message
                        message_dict['name'] = config_alert_data['message'].format(object=row)

                        # user_ids
                        if user_field_id:
                            message_dict['user_id'] = row[user_field_id].id
                        elif row.__hasattr__('create_uid'):
                            message_dict['user_id'] = row.create_uid.id
                        elif row.__hasattr__('user_id'):
                            message_dict['user_id'] = row.user_id.id
                        else:
                            message_dict['user_id'] = uid

                        if not message_dict.get('user_id'):
                            continue

                        # user_ids
                        message_dict['user_ids'] = [[6, 0, list(set([message_dict['user_id'], row.user_id.id]))]]
                        # model
                        message_dict['model_id'] = config_alert_data['model_id'][0]
                        # id alert message
                        message_dict['alert_config_id'] = config_alert_data['id']
                        # object id
                        message_dict['ids'] = target_id
                        # type message
                        message_dict['type'] = config_alert_data['type']
                        # for create, 'state' always in 'open'
                        message_dict['state'] = 'open'
                        # is Child of other family message ?
                        bool_is_child = False
                        if config_alert_data['parent_id']:
                            bool_is_child = True
                        message_dict['is_child'] = bool_is_child

                        # compose link
                        # link_string = '{0[server]}/web/webclient/home#model={0[model]}&id={0[model_id]}'
                        # link_dict = {'server': host_data['value'], 'model': obj_model_data['model'],
                        #              'model_id': target_id}
                        message_dict['link'] = "{},{}".format(obj_model_data['model'], target_id)

                        # manage e-mails
                        if config_alert_data['flag_email']:
                            # compose e-mail message
                            message_dict['email_message'] = config_alert_data['email_message'].format(object=row)
                            # search e_mail address of partner_id
                            emails = ''
                            for email_address in row.partner_id.address:
                                if email_address.email not in ([], False, ''):
                                    emails = email_address.email
                                    break

                            # adding user creator document ?
                            if config_alert_data['add_user_creator']:
                                user_id = 0
                                if row.__hasattr__('create_uid'):
                                    user_id = row.create_uid.id
                                elif row.__hasattr__('user_id'):
                                    user_id = row.user_id.id
                                if user_id not in (0, [], False, ''):
                                    user_create_data = res_users_model.read(cr, uid, user_id, context=context)
                                    if user_create_data['user_email']:
                                        if emails in ([], False, ''):
                                            emails = user_create_data['user_email']
                                        else:
                                            emails = '%s, %s' % (emails, user_create_data['user_email'])
                            message_dict['mail_addresses'] = emails
                            # compose e-mail subject
                            message_dict['subject'] = config_alert_data['subject'].format(row)
                        self.create(cr, uid, message_dict, context)
            else:
                # parents message
                if config_alert_data['is_parent']:
                    num_child_message = 0
                    exist_records_child = False
                    child_config_message_ids = alert_config_model.search(cr, uid,
                                                                       [('parent_id', '=', config_alert_data['id'])])
                    if child_config_message_ids:
                        child_message_ids = ir_alert_model.search(cr, uid,
                                                             [('alert_config_id', '=', child_config_message_ids[0]),
                                                              ('state', '=', 'open')])
                        if child_message_ids:
                            exist_records_child = True
                            num_child_message = len(child_message_ids)

                    exist_record_parent = False
                    parent_message_ids = ir_alert_model.search(cr, uid, [('alert_config_id', '=', config_alert_data['id'])])
                    if parent_message_ids:
                        exist_record_parent = True

                    if exist_records_child:
                        message_dict = {
                            'model_id': config_alert_data['model_id'][0],
                            'name': config_alert_data['message'].format(object=num_child_message),
                            'user_id': uid,
                            'user_ids': [[6, 0, row.user_id.id]],
                            'alert_config_id': config_alert_data['id'],
                            'type': config_alert_data['type'],
                            'state': 'open',
                        }

                        link_string = '{0[server]}/web/webclient/home#model={0[model]}&view_type=list&title=Alerts&page=0&action_id={0[action_id]}'
                        link_dict = {'server': host_data['value'], 'model': obj_model_data['model'],
                                     'action_id': config_alert_data['action_id']}
                        message_dict['link'] = link_string.format(link_dict)
                        if exist_record_parent:
                            self.write(cr, uid, parent_message_ids[0], message_dict, context=context)
                        else:
                            self.create(cr, uid, message_dict, context)
                    else:
                        if exist_record_parent:
                            message_dict = {
                                'state': 'done'
                            }
                            self.write(cr, uid, parent_message_ids[0], message_dict, context=context)

            to_remove_ids = self.search(cr, uid, [('model_id', '=', config_alert_data['model_id'][0]),
                                                  ('ids', 'not in', target_model_ids), ('state', '=', 'open')],
                                        context=context)
            self.write(cr, 1, to_remove_ids, {'state': 'done'}, context)

        return True

    # control model's message (change state) and relative change state messages
    def control_state_message(self, cr, uid, context=None):
        obj_alert = self.pool['ir.alert']
        obj_alert_config = self.pool['ir.alert.config']
        obj_model = self.pool['ir.model']

        # alert's data
        obj_alert_ids = obj_alert.search(cr, uid, [('state', '=', 'open')], context=context)
        obj_alert_datas = obj_alert.read(cr, uid, obj_alert_ids, context=context)

        for obj_alert_data in obj_alert_datas:
            obj_config_alert_datas = obj_alert_config.read(cr, uid, obj_alert_data['alert_config_id'][0],
                                                           context=context)

            if obj_config_alert_datas and (not obj_config_alert_datas['is_parent']):
                # search object from object model
                obj_model_data = obj_model.read(cr, uid, obj_config_alert_datas['model_id'][0], context=context)
                examine_obj = self.pool.get(obj_model_data['model'])

                # search id of model
                position_field = obj_alert_data['link'].find('id=')
                if position_field == -1:
                    obj_object_id = position_field
                else:
                    position_field += 3
                    obj_object_id = int(obj_alert_data['link'][position_field:])

                if obj_object_id != -1:
                    obj_examine_data = examine_obj.read(cr, uid, obj_object_id, ['state'], context=context)
                    # control state for change
                    update_state_done = False
                    if obj_config_alert_datas['flag_not_state']:
                        if obj_examine_data['state'] == obj_config_alert_datas['state_comparison']:
                            update_state_done = True
                    else:
                        if (obj_examine_data and obj_config_alert_datas) and (
                                obj_examine_data['state'] != obj_config_alert_datas['state_comparison']):
                            update_state_done = True

                    # change state message
                    if update_state_done:
                        update_dict = {
                            'state': 'done'
                        }
                        obj_alert.write(cr, uid, obj_alert_data['id'], update_dict, context=context)

        return True
        
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        types = {
            'out_invoice': 'CI: ',
            'in_invoice': 'SI: ',
            'out_refund': 'OR: ',
            'in_refund': 'SR: ',
        }
        return [(r['id'], (r['number']) or types[r['type']] + (r['name'] or '')) for r in self.read(cr, uid, ids, ['type', 'number', 'name'], context, load='_classic_write')]

    def read(self, cr, uid, ids, fields_read=None, context=None, load='_classic_read'):
        res = super(ir_alert, self).read(cr, uid, ids, fields_read, context, load)

        # obj_fake = self.pool.get('fake.ir.alert')
        # obj_alert_config = self.pool.get('ir.alert.config')
        #
        # fields_to_read = ['name', 'user_id', 'type', 'state', 'is_child', 'alert_config_id', 'link', 'note', 'mail_addresses', 'subject', 'email_message']
        # res = super(ir_alert, self).read(cr, uid, ids, fields_to_read, context, load)
        #
        # obj_fake_ids = obj_fake.search(cr, uid, [])
        # if len(obj_fake_ids) > 0:
        #     for record_id in obj_fake_ids:
        #         obj_fake.unlink(cr, uid, record_id, context=context)
        #
        # if len(ids) == 1:
        #     data_record = res[0]
        #
        #     enter = False
        #     if 'is_child' in data_record:
        #         if not data_record['is_child']:
        #             enter = True
        #     else:
        #         enter = True
        #
        #     if enter:
        #         alert_config_data = obj_alert_config.read(cr, uid, data_record['alert_config_id'][0], context=context)
        #         if alert_config_data['is_parent']:
        #             child_config_ids = obj_alert_config.search(cr, uid, [('parent_id', '=', data_record['alert_config_id'][0])])
        #             if len(child_config_ids) > 0:
        #                 list_child_records_ids = []
        #                 for child_config_id in child_config_ids:
        #                     list_child_ids = super(ir_alert, self).search(cr, uid, [('alert_config_id', '=', child_config_id), ('state', '=', 'open')])
        #                     list_child_records_ids = list_child_records_ids + list_child_ids
        #                 for child_record_id in list_child_records_ids:
        #                     child_data = super(ir_alert, self).read(cr, uid, child_record_id, fields_to_read, context, load)
        #                     fake_record = {
        #                         'alert_id': child_data['id'],
        #                         'name': child_data['name'],
        #                         'user_id': child_data['user_id'][0],
        #                         'type': child_data['type'],
        #                         'link': child_data['link'],
        #                         'note': child_data['note'],
        #                         'mail_addresses': child_data['mail_addresses'],
        #                         'subject': child_data['subject'],
        #                         'email_message': child_data['email_message'],
        #                         'state': child_data['state'],
        #                     }
        #                     obj_fake.create(cr, uid, fake_record, context)
        return res

