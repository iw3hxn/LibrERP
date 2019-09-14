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
#from datetime import date
from datetime import timedelta
import pytz

from osv import fields, osv
from tools.translate import _


class fake_ir_alert(osv.osv):

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
        my_records = super(fake_ir_alert, self).read(cr, uid, ids, ['name', 'alert_id', 'id'], context, load)
        if my_records not in ([], False, ''):
            list_not_deleted_ids = []
            for my_record in my_records:
                if my_record['alert_id'] in list_not_deleted_ids:
                    super(fake_ir_alert, self).unlink(cr, uid, my_record['id'], context=context)
                else:
                    list_not_deleted_ids = list_not_deleted_ids + [my_record['alert_id']]
        res = super(fake_ir_alert, self).read(cr, uid, ids, fields_to_read, context, load)
        return res

    def browse_ftp(self, cr, uid, ids, context=None):
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

fake_ir_alert()


class ir_alert(osv.osv):

    _name = "ir.alert"
    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=256, required=True),
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
    }
    _defaults = {
        'state': 'open',
        'type': 'warning',
        'user_id': lambda self, cr, uid, context: uid,
    }

    def create(self, cr, uid, vals, context=None):
        return super(ir_alert, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        return super(ir_alert, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        res = super(ir_alert, self).unlink(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'cancel'})
        return res
   
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        
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
        obj_fake = self.pool.get('fake.ir.alert')
        obj_alert_config = self.pool.get('ir.alert.config')

        fields_to_read = ['name', 'user_id', 'type', 'state', 'is_child', 'alert_config_id', 'link', 'note', 'mail_addresses', 'subject', 'email_message']
        res = super(ir_alert, self).read(cr, uid, ids, fields_to_read, context, load)

        obj_fake_ids = obj_fake.search(cr, uid, [])
        if len(obj_fake_ids) > 0:
            for record_id in obj_fake_ids:
                obj_fake.unlink(cr, uid, record_id, context=context)
        obj_fake_ids = obj_fake.search(cr, uid, [])

        if len(ids) == 1:
            data_record = res[0]

            enter = False
            if 'is_child' in data_record:
                if not data_record['is_child']:
                    enter = True
            else:
                enter = True
            
            if enter:
                alert_config_data = obj_alert_config.read(cr, uid, data_record['alert_config_id'][0], context=context)
                if alert_config_data['is_parent']:
                    child_config_ids = obj_alert_config.search(cr, uid, [('parent_id', '=', data_record['alert_config_id'][0])])
                    if len(child_config_ids) > 0:
                        list_child_records_ids = []
                        for child_config_id in child_config_ids:
                            list_child_ids = super(ir_alert, self).search(cr, uid, [('alert_config_id', '=', child_config_id), ('state', '=', 'open')])
                            list_child_records_ids = list_child_records_ids + list_child_ids
                        for child_record_id in list_child_records_ids:
                            fake_record = {}
                            child_data = super(ir_alert, self).read(cr, uid, child_record_id, fields_to_read, context, load)
                            fake_record['alert_id'] = child_data['id']
                            fake_record['name'] = child_data['name']
                            fake_record['user_id'] = child_data['user_id'][0]
                            fake_record['type'] = child_data['type']
                            fake_record['link'] = child_data['link']
                            fake_record['note'] = child_data['note']
                            fake_record['mail_addresses'] = child_data['mail_addresses']
                            fake_record['subject'] = child_data['subject']
                            fake_record['email_message'] = child_data['email_message']
                            fake_record['state'] = child_data['state']
                            obj_fake.create(cr, uid, fake_record, context)
        return res
ir_alert()


class ir_alert_states(osv.osv):

    _name = "ir.alert.states"
    _columns = {
        'model_id': fields.many2one('ir.model', 'Object'),
        'name': fields.char('State name', size=60),
        'value': fields.char('State value', size=60),
    }
ir_alert_states()


class ir_alert_config(osv.osv):
    _name = "ir.alert.config"

    #create 'state' for comparison
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        obj_model = self.pool.get('ir.model')
        obj_alert_states = self.pool.get('ir.alert.states')
        result = super(ir_alert_config, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        if (result['type'] == 'form') and ('toolbar' in result):
            model_ids = obj_model.search(cr, uid, [])
            model_datas = obj_model.browse(cr, uid, model_ids)
            for model_data in model_datas:
                examine_obj_data = self.pool.get(model_data.model)
                if hasattr(examine_obj_data, 'fields_get'):
                    examine_obj_fields = examine_obj_data.fields_get(cr, uid, context=context)
                    if 'state' in examine_obj_fields:
                        if 'selection' in examine_obj_fields['state']:
                            for value in examine_obj_fields['state']['selection']:
                                exist_ids = obj_alert_states.search(cr, uid, [('model_id', '=', model_data.id), ('value', '=', value[0])])
                                if exist_ids in ([], False, ''):
                                    dict_result = {}
                                    dict_result['model_id'] = model_data.id
                                    dict_result['name'] = value[1]
                                    dict_result['value'] = value[0]
                                    obj_alert_states.create(cr, uid, dict_result, context)
        return result

    # correct 'model' (ir.model) for 'parent message'
    def onchange_model_id(self, cr, uid, ids, is_parent, context=None):
        obj_model = self.pool.get('ir.model')
        if is_parent:
            parent_model_ids = obj_model.search(cr, uid, [('name', '=', 'ir.alert')])
            return_value = {'model_id': parent_model_ids[0]}
        else:
            return_value = {'model_id': False}
        return {'value': return_value}

    #filter for 'state' (only 'state' of model in field 'model_id')
    def model_id_change(self, cr, uid, ids, model_id, context=None):
        res = {'domain': {'state_id': []}}
        if model_id:
            obj_alert_states = self.pool.get('ir.alert.states')
            alert_states_ids = obj_alert_states.search(cr, uid, [('model_id', '=', model_id)])
            res = {'domain': {'state_id': [('id', 'in', alert_states_ids)]}}
        return res

    #value of 'state' for comparison
    def state_change(self, cr, uid, ids, state_id, context=None):
        obj_alert_states = self.pool.get('ir.alert.states')
        res_final = {'value': {}}
        if state_id not in ([], False, '', 0, -1):
            state_data = obj_alert_states.read(cr, uid, state_id, ['model_id', 'name', 'value'], context=context)
            res_final['value'] = {'state_comparison': state_data['value']}
        return res_final

    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'model_id': fields.many2one('ir.model', 'Object', required=True),
        'type': fields.selection([('warning', 'Warning'), ('activity', 'Activity')], 'Type Alert', required=True),
        'is_parent': fields.boolean('Is Parent?'),
        'parent_id': fields.many2one('ir.alert.config', 'Parent Message', select=True, ondelete='cascade'),
        'action_id': fields.integer('Action View'),
        'offset': fields.integer('Hours Offset'),
        'flag_not_state': fields.boolean('NOT State'),
        'state_id': fields.many2one('ir.alert.states', 'State'),
        'state_comparison': fields.char('State Comparison', size=60),
        'date_comparison_field_id': fields.many2one('ir.model.fields', 'Comparison Date field', domain="['&',('ttype', 'in', ('date','datetime')),('model_id', '=', model_id)]"),
        'message': fields.char('Message', size=256, required=True),
        'flag_email': fields.boolean('Send Message in email?'),
        'subject': fields.char('Subject', size=256),
        'email_message': fields.text('Message of the Mail'),
        'add_user_creator': fields.boolean("add address user document's creator?"),
    }
    _defaults = {
        'type': 'activity',
        'offset': 0,
        'is_parent': False,
        'flag_email': False,
    }

    def create(self, cr, uid, vals, context=None):
        obj_model = self.pool.get('ir.model')
        obj_fields = self.pool.get('ir.model.fields')
        obj_actions = self.pool.get('ir.actions.actions')
        
        #control message
        message = vals['message']
        number = message.count('{')

        close_fields = message.count('}')
        if number != close_fields:
            raise osv.except_osv(_('Error'), _("missing curly brackets in alert message."))

        for counter in range(0, number):
            position_ini = message.find('{')
            position_fin = message.find('}')
            
            first_control = message[position_ini + 1: position_ini + 7]
            if first_control not in ('object'):
                string_in_error = message[position_ini - 1: position_fin + 1]
                raise osv.except_osv(_('Error'), _('Value not valid for ' + string_in_error + ". Valid value is 'object', for parent message (number record) or 'object.<name field>' for object field, in alert message."))

            if first_control == 'object':
                second_control = message[position_ini + 7: position_ini + 8]
                if second_control not in ('}', '.'):
                    string_in_error = message[position_ini - 1: position_fin + 1]
                    raise osv.except_osv(_('Error'), _('Value not valid for ' + string_in_error + ". Missing dot or '}' in alert message."))

            #obj_model_data = obj_model.read(cr, uid, vals['model_id'], ['model'], context=context)
            #examine_obj = self.pool.get(obj_model_data['model'])
            fields = (message[position_ini + 1: position_fin]).split('.')
            temp_id = vals['model_id']
            count_fields = 0
            total_fields = len(fields)
            for field in fields:
                count_fields += 1
                if field != 'object':
                    fields_ids = obj_fields.search(cr, uid, [('model_id', '=', temp_id), ('name', '=', field)])
                    if fields_ids:
                        fields_data = obj_fields.read(cr, uid, fields_ids[0], ['relation'], context=context)
                    else:
                        raise osv.except_osv(_('Error'), _('Value not valid for ' + message[position_ini + 1: position_fin] + ". field not in object, in alert message."))
                    if fields_data['relation']:
                        temp_ids = obj_model.search(cr, uid, [('model', '=', fields_data['relation'])])
                        temp_id = temp_ids[0]
                    else:
                        if count_fields != total_fields:
                            raise osv.except_osv(_('Error'), _('Value not valid for ' + message[position_ini + 1: position_fin] + ". field not in object, in alert message."))
              
            message = message[position_fin + 1:]

        #control E-Mail message
        if ('flag_email' in vals) and (vals['flag_email']):
            email_message = vals['email_message']
            number = email_message.count('{')

            close_fields = email_message.count('}')
            if number != close_fields:
                raise osv.except_osv(_('Error'), _("missing curly brackets in 'E-Mail's message'."))

            for counter in range(0, number):
                position_ini = email_message.find('{')
                position_fin = email_message.find('}')

                first_control = email_message[position_ini + 1: position_ini + 7]
                if first_control not in ('object'):
                    string_in_error = email_message[position_ini - 1: position_fin + 1]
                    raise osv.except_osv(_('Error'), _('Value not valid for ' + string_in_error + ". Valid value is 'object', for parent message (number record) or 'object.<name field>' for object field, in E-Mail message."))

                if first_control == 'object':
                    second_control = email_message[position_ini + 7: position_ini + 8]
                    if second_control not in ('}', '.'):
                        string_in_error = email_message[position_ini - 1: position_fin + 1]
                        raise osv.except_osv(_('Error'), _('Value not valid for ' + string_in_error + ". Missing dot or '}' in E-Mail message."))

            #obj_model_data = obj_model.read(cr, uid, vals['model_id'], ['model'], context=context)
            #examine_obj = self.pool.get(obj_model_data['model'])
            fields = (email_message[position_ini + 1: position_fin]).split('.')
            temp_id = vals['model_id']
            count_fields = 0
            total_fields = len(fields)
            for field in fields:
                count_fields += 1
                if field != 'object':
                    fields_ids = obj_fields.search(cr, uid, [('model_id', '=', temp_id), ('name', '=', field)])
                    if fields_ids:
                        fields_data = obj_fields.read(cr, uid, fields_ids[0], ['relation'], context=context)
                    else:
                        raise osv.except_osv(_('Error'), _('Value not valid for ' + email_message[position_ini + 1: position_fin] + ". field not in object, in E-Mail message."))
                    if fields_data['relation']:
                        temp_ids = obj_model.search(cr, uid, [('model', '=', fields_data['relation'])])
                        temp_id = temp_ids[0]
                    else:
                        if count_fields != total_fields:
                            raise osv.except_osv(_('Error'), _('Value not valid for ' + email_message[position_ini + 1: position_fin] + ". field not in object, in E-Mail message."))

                email_message = email_message[position_fin + 1:]

        #search actions id
        if ('is_parent' in vals) and (vals['is_parent']):
            actions_ids = obj_actions.search(cr, uid, [('name', '=', 'Family Alerts')])
            if actions_ids not in ([], False, ''):
                vals['action_id'] = actions_ids[0]
            else:
                if 'action_id' in vals:
                    del vals['action_id']

        return super(ir_alert_config, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        obj_fields = self.pool.get('ir.model.fields')
        obj_model = self.pool.get('ir.model')
        obj_config = self.pool.get('ir.alert.config').read(cr, uid, ids[0], ['model_id'], context=context)
        obj_actions = self.pool.get('ir.actions.actions')
            
        if 'message' in vals.keys():
            #control message
            message = vals['message']
            number = message.count('{')

            close_fields = message.count('}')
            if number != close_fields:
                raise osv.except_osv(_('Error'), _("missing curly brackets in alert message."))

            for counter in range(0, number):
                position_ini = message.find('{')
                position_fin = message.find('}')

                first_control = message[position_ini + 1: position_ini + 7]
                if first_control not in ('object'):
                    string_in_error = message[position_ini - 1: position_fin + 1]
                    raise osv.except_osv(_('Error'), _('Value not valid for ' + string_in_error + ". Valid value is 'object', for parent message (number record) or 'object.<name field>' for object field, in alert message."))

                if first_control == 'object':
                    second_control = message[position_ini + 7: position_ini + 8]
                    if second_control not in ('}', '.'):
                        string_in_error = message[position_ini - 1: position_fin + 1]
                        raise osv.except_osv(_('Error'), _('Value not valid for ' + string_in_error + ". Missing dot or '}' in alert message."))

                #obj_model_data = obj_model.read(cr, uid, vals['model_id'], ['model'], context=context)
                #examine_obj = self.pool.get(obj_model_data['model'])
                fields = (message[position_ini + 1: position_fin]).split('.')
                if 'model_id' in vals:
                    temp_id = vals['model_id']
                else:
                    temp_id = obj_config['model_id'][0]
                count_fields = 0
                total_fields = len(fields)
                for field in fields:
                    count_fields += 1
                    if field != 'object':
                        fields_ids = obj_fields.search(cr, uid, [('model_id', '=', temp_id), ('name', '=', field)])
                        if fields_ids:
                            fields_data = obj_fields.read(cr, uid, fields_ids[0], ['relation'], context=context)
                        else:
                            raise osv.except_osv(_('Error'), _('Value not valid for ' + message[position_ini + 1: position_fin] + ". field not in object, in alert message."))
                        if fields_data['relation']:
                            temp_ids = obj_model.search(cr, uid, [('model', '=', fields_data['relation'])])
                            temp_id = temp_ids[0]
                        else:
                            if count_fields != total_fields:
                                raise osv.except_osv(_('Error'), _('Value not valid for ' + message[position_ini + 1: position_fin] + ". field not in object, in alert message."))

                message = message[position_fin + 1:]

        #control E-Mail message
        if 'email_message' in vals.keys():
            email_message = vals['email_message']
            number = email_message.count('{')

            close_fields = email_message.count('}')
            if number != close_fields:
                raise osv.except_osv(_('Error'), _("missing curly brackets in 'E-Mail's message'."))

            for counter in range(0, number):
                position_ini = email_message.find('{')
                position_fin = email_message.find('}')

                first_control = email_message[position_ini + 1: position_ini + 7]
                if first_control not in ('object'):
                    string_in_error = email_message[position_ini - 1: position_fin + 1]
                    raise osv.except_osv(_('Error'), _('Value not valid for ' + string_in_error + ". Valid value is 'object', for parent message (number record) or 'object.<name field>' for object field, in E-Mail message."))

                if first_control == 'object':
                    second_control = email_message[position_ini + 7: position_ini + 8]
                    if second_control not in ('}', '.'):
                        string_in_error = email_message[position_ini - 1: position_fin + 1]
                        raise osv.except_osv(_('Error'), _('Value not valid for ' + string_in_error + ". Missing dot or '}' in E-Mail message."))

                #obj_model_data = obj_model.read(cr, uid, vals['model_id'], ['model'], context=context)
                #examine_obj = self.pool.get(obj_model_data['model'])
                fields = (email_message[position_ini + 1: position_fin]).split('.')
                if 'model_id' in vals:
                    temp_id = vals['model_id']
                else:
                    temp_id = obj_config['model_id'][0]
                count_fields = 0
                total_fields = len(fields)
                for field in fields:
                    count_fields += 1
                    if field != 'object':
                        fields_ids = obj_fields.search(cr, uid, [('model_id', '=', temp_id), ('name', '=', field)])
                        if fields_ids:
                            fields_data = obj_fields.read(cr, uid, fields_ids[0], ['relation'], context=context)
                        else:
                            raise osv.except_osv(_('Error'), _('Value not valid for ' + email_message[position_ini + 1: position_fin] + ". field not in object, in E-Mail message."))
                        if fields_data['relation']:
                            temp_ids = obj_model.search(cr, uid, [('model', '=', fields_data['relation'])])
                            temp_id = temp_ids[0]
                        else:
                            if count_fields != total_fields:
                                raise osv.except_osv(_('Error'), _('Value not valid for ' + email_message[position_ini + 1: position_fin] + ". field not in object, in E-Mail message."))

                email_message = email_message[position_fin + 1:]

        #search actions id
        if ('is_parent' in vals) and (vals['is_parent']):
            actions_ids = obj_actions.search(cr, uid, [('name', '=', 'Family Alerts')])
            if actions_ids not in ([], False, ''):
                vals['action_id'] = actions_ids[0]
            else:
                if 'action_id' in vals:
                    del vals['action_id']

        return super(ir_alert_config, self).write(cr, uid, ids, vals, context=context)

ir_alert_config()


class inherit_ir_alert(osv.osv):
    _inherit = 'ir.alert'
    _columns = {
        'alert_config_id': fields.many2one('ir.alert.config', 'Message Config index'),
    }

    def browse_ftp(self, cr, uid, ids, context=None):
        alert_data = self.read(cr, uid, ids, context=context)
        return {'type': 'ir.actions.act_url', 'url': alert_data[0]['link'], 'target': 'new'}

    def button_send_mail(self, cr, uid, ids, context=None):
        obj_user = self.pool.get('res.users')
        obj_mail = self.pool.get('mail.compose.message')
        
        email_dict = {}
        if ('uid' in context):
            my_data = obj_user.read(cr, uid, context['uid'], context=context)
        
        if ('user_email' in my_data) and (my_data['user_email']):
            email_dict['email_from'] = my_data['user_email']
        else:
            raise osv.except_osv(_('Error'), _("Your E-Mail (message Sender), not valid. Valorize your exactly E-Mail address, please."))
            return False
        email_dict['email_to'] = context['mail_addresses']
        email_dict['subject'] = context['subject']
        email_dict['body_text'] = context['email_message']
        email_id = obj_mail.create(cr, uid, email_dict, context)
       
        obj_mail.send_mail(cr, uid, [email_id], context={'mail.compose.message.mode': ''})
        return True

    # create and management of message (cron's routine)
    def manage_alerts(self, cr, uid, ids=False, context=None):
        # control change model' state
        self.control_state_message(cr, uid, ids, context)

        obj_alert_config = self.pool.get('ir.alert.config')
        obj_alert = self.pool.get('ir.alert')
        obj_model = self.pool.get('ir.model')
        obj_fields = self.pool.get('ir.model.fields')
        #obj_ir_alert = self.pool.get('ir.alert.fields')
        obj_user = self.pool.get('res.users')
        obj_config_parameter = self.pool.get('ir.config_parameter')
        #obj_send_mails = self.pool.get('mail.compose.message')
        user_admin_id = obj_user.search(cr, uid, [('name', '=', 'Administrator')])

        # my server and port
        host_ids = obj_config_parameter.search(cr, uid, [('key', '=', 'web.base.url')])
        host_data = obj_config_parameter.read(cr, uid, host_ids[0], context=context)

        #object's data
        obj_alert_ids = obj_alert_config.search(cr, uid, [])
        obj_alert_data = obj_alert_config.read(cr, uid, obj_alert_ids, context=context)
 
        #generate message
        for config_alert_data in obj_alert_data:
            obj_model_data = obj_model.read(cr, uid, config_alert_data['model_id'][0], context=context)
            if (config_alert_data['date_comparison_field_id'] not in ([], False, '')) or (config_alert_data['state_comparison'] not in ([], False, '')):
                condition = []
                if config_alert_data['date_comparison_field_id'] not in ([], False, ''):
                    obj_fields_data = obj_fields.read(cr, uid, config_alert_data['date_comparison_field_id'][0], context=context)

                    # correct date
                    access_user_data = obj_user.read(cr, uid, uid, context=context)
                    if 'context_tz' in access_user_data:
                        if access_user_data['context_tz'] not in ('', False, None, 0, []):
                            local_timezone = pytz.timezone(access_user_data['context_tz'])
                        else:
                            local_timezone = pytz.timezone('UTC')
                    else:
                        local_timezone = pytz.timezone('UTC')
                    utc_timezone = pytz.timezone('UTC')
                    datetime_offset = utc_timezone.localize(datetime.now() - timedelta(hours=config_alert_data['offset']))
                    datetime_offset = datetime_offset.astimezone(local_timezone)
                    date_offset = datetime_offset.date()
                    name_field_date = obj_fields_data['name']
                    name_field_date = str(name_field_date)
                    if obj_fields_data['ttype'] == 'date':
                        date_offset_str = date_offset.strftime("%Y-%m-%d")
                        condition = condition + [(name_field_date, '=', date_offset_str)]
                    else:
                        start_period = datetime_offset.replace(hour=0)
                        start_period = start_period.replace(minute=0)
                        start_period = start_period.replace(second=0)
                        start_period = start_period.replace(microsecond=0)
                        start_period_str = unicode(start_period)
                        start_period_str = str(start_period_str)
                        end_period = datetime_offset.replace(hour=23)
                        end_period = end_period.replace(minute=59)
                        end_period = end_period.replace(second=59)
                        end_period = end_period.replace(microsecond=999999)
                        end_period_str = unicode(end_period)
                        end_period_str = str(end_period_str)
                        condition = condition + [(name_field_date, '>=', start_period_str)]
                        condition = condition + [(name_field_date, '<=', end_period_str)]

                if config_alert_data['state_comparison'] not in ([], False, ''):
                    state_comparison = str(config_alert_data['state_comparison'])
                    if config_alert_data['flag_not_state']:
                        condition = condition + [('state', '!=', state_comparison)]
                    else:
                        condition = condition + [('state', '=', state_comparison)]

                examine_obj = self.pool.get(obj_model_data['model'])
                examine_obj_ids = examine_obj.search(cr, uid, condition, context=context)
                #ids_existing_record = obj_alert.search(cr, uid, [('alert_config_id', '=', config_alert_data['id']), ('state', '=', 'open')], context=context)
                
                # existing message?
                for examine_obj_id in examine_obj_ids:
                    existing_message = self.search(cr, uid, [('model_id', '=', config_alert_data['model_id'][0]), ('ids', '=', examine_obj_id)], context=context)
                    if not existing_message:     # not exists: create message
                        message_dict = {}
                        # read object
                        row = examine_obj.browse(cr, uid, examine_obj_id, context=context)
                        # compose name message
                        message_dict['name'] = config_alert_data['message'].format(object=row)
                        
                        # user_ids
                        if row.__hasattr__('create_uid'):
                            message_dict['user_id'] = row.create_uid.id
                        elif row.__hasattr__('user_id'):
                            message_dict['user_id'] = row.user_id.id
                        else:
                            message_dict['user_id'] = uid
                        # user_ids
                        message_dict['user_ids'] = [[6, 0, user_admin_id]]
                        # model
                        message_dict['model_id'] = config_alert_data['model_id'][0]
                        # id alert message
                        message_dict['alert_config_id'] = config_alert_data['id']
                        # object id
                        message_dict['ids'] = examine_obj_id
                        # type message
                        message_dict['type'] = config_alert_data['type']
                        # for create, 'state' always in 'open'
                        message_dict['state'] = 'open'
                        # is Child of othe family message ?
                        bool_is_child = False
                        if config_alert_data['parent_id'] not in ([], False, ''):
                            bool_is_child = True
                        message_dict['is_child'] = bool_is_child

                        # compose link
                        link_string = '{0[server]}/web/webclient/home#model={0[model]}&id={0[model_id]}'
                        link_dict = {'server': host_data['value'], 'model': obj_model_data['model'], 'model_id': examine_obj_id}
                        message_dict['link'] = link_string.format(link_dict)
                        
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
                                    user_create_data = obj_user.read(cr, uid, user_id, context=context)
                                    if user_create_data['user_email'] not in ([], False, ''):
                                        if emails in ([], False, ''):
                                            emails = user_create_data['user_email']
                                        else:
                                            emails = '%s, %s' % (emails, user_create_data['user_email'])
                            message_dict['mail_addresses'] = emails
                            # compose e-mail subject
                            message_dict['subject'] = config_alert_data['subject'].format(row)
                        self.create(cr, uid, message_dict, context)
            else:
                #parents message
                if config_alert_data['is_parent']:
                    num_child_message = 0
                    exist_records_child = False
                    child_config_message_ids = obj_alert_config.search(cr, uid, [('parent_id', '=', config_alert_data['id'])])
                    if child_config_message_ids not in ([], False, ''):
                        child_message_ids = obj_alert.search(cr, uid, [('alert_config_id', '=', child_config_message_ids[0]), ('state', '=', 'open')])
                        if child_message_ids not in ([], False, ''):
                            exist_records_child = True
                            num_child_message = len(child_message_ids)

                    exist_record_parent = False
                    parent_message_ids = obj_alert.search(cr, uid, [('alert_config_id', '=', config_alert_data['id'])])
                    if parent_message_ids not in ([], False, ''):
                        exist_record_parent = True
                        
                    if exist_records_child:
                        message_dict = {}
                        message_dict['model_id'] = config_alert_data['model_id'][0]
                        message_dict['name'] = config_alert_data['message'].format(object=num_child_message)
                        message_dict['user_id'] = uid
                        message_dict['user_ids'] = [[6, 0, user_admin_id]]
                        message_dict['alert_config_id'] = config_alert_data['id']
                        message_dict['type'] = config_alert_data['type']
                        message_dict['state'] = 'open'
                        link_string = '{0[server]}/web/webclient/home#model={0[model]}&view_type=list&title=Alerts&page=0&action_id={0[action_id]}'
                        link_dict = {'server': host_data['value'], 'model': obj_model_data['model'], 'action_id': config_alert_data['action_id']}
                        message_dict['link'] = link_string.format(link_dict)
                        if exist_record_parent:
                            self.write(cr, uid, parent_message_ids[0], message_dict, context=context)
                        else:
                            self.create(cr, uid, message_dict, context)
                    else:
                        if exist_record_parent:
                            message_dict = {}
                            message_dict['state'] = 'done'
                            self.write(cr, uid, parent_message_ids[0], message_dict, context=context)
        return True

    # control model's message (change state) and relative change state messages
    def control_state_message(self, cr, uid, ids=False, context=None):
        obj_alert = self.pool['ir.alert']
        obj_alert_config = self.pool['ir.alert.config']
        obj_model = self.pool['ir.model']

        #alert's data
        obj_alert_ids = obj_alert.search(cr, uid, [('state', '=', 'open')], context=context)
        obj_alert_datas = obj_alert.read(cr, uid, obj_alert_ids, context=context)

        for obj_alert_data in obj_alert_datas:
            obj_config_alert_datas = obj_alert_config.read(cr, uid, obj_alert_data['alert_config_id'][0], context=context)
            
            
            if obj_config_alert_datas and (not obj_config_alert_datas['is_parent']):
                # search object from object model
                obj_model_data = obj_model.read(cr, uid, obj_config_alert_datas['model_id'][0], context=context)
                examine_obj = self.pool.get(obj_model_data['model'])

                #search id of model
                position_field = obj_alert_data['link'].find('id=')
                if position_field == -1:
                    obj_object_id = position_field
                else:
                    position_field += 3
                    obj_object_id = int(obj_alert_data['link'][position_field:])

                if obj_object_id != -1:
                    obj_examine_data = examine_obj.read(cr, uid, obj_object_id, ['state'], context=context)
                    #control state for change
                    update_state_done = False
                    if obj_config_alert_datas['flag_not_state']:
                        if obj_examine_data['state'] == obj_config_alert_datas['state_comparison']:
                            update_state_done = True
                    else:
                        if (obj_examine_data and obj_config_alert_datas) and (obj_examine_data['state'] != obj_config_alert_datas['state_comparison']):
                            update_state_done = True

                    # change state message
                    if update_state_done:
                        update_dict = {}
                        update_dict['state'] = 'done'
                        obj_alert.write(cr, uid, obj_alert_data['id'], update_dict, context=context)

        return True
