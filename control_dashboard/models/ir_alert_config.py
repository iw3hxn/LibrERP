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

# from datetime import date

from tools.translate import _

from openerp.osv import orm, fields


class ir_alert_config(orm.Model):
    _name = "ir.alert.config"

    # create 'state' for comparison
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        ir_model_model = self.pool['ir.model']
        ir_alert_states_model = self.pool['ir.alert.states']
        result = super(ir_alert_config, self).fields_view_get(cr, uid, view_id, view_type, context=context,
                                                              toolbar=toolbar, submenu=submenu)
        if (result['type'] == 'form') and ('toolbar' in result):
            model_ids = ir_model_model.search(cr, uid, [('osv_memory', '=', False)])

            for model_data in ir_model_model.browse(cr, uid, model_ids, context):
                if not model_data._model._auto:
                    continue
                examine_obj_data = self.pool.get(model_data.model)
                if hasattr(examine_obj_data, 'fields_get'):
                    examine_obj_fields = examine_obj_data.fields_get(cr, uid, context=context)
                    if 'state' in examine_obj_fields:
                        if 'selection' in examine_obj_fields['state']:
                            for value in examine_obj_fields['state']['selection']:
                                exist_ids = ir_alert_states_model.search(cr, uid, [('model_id', '=', model_data.id),
                                                                                   ('value', '=', value[0])])
                                if not exist_ids:
                                    dict_result = {
                                        'model_id': model_data.id,
                                        'name': value[1],
                                        'value': value[0]
                                    }
                                    ir_alert_states_model.create(cr, uid, dict_result, context)
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

    # filter for 'state' (only 'state' of model in field 'model_id')
    def model_id_change(self, cr, uid, ids, model_id, context=None):
        res = {'domain': {'state_id': []}}
        if model_id:
            obj_alert_states = self.pool['ir.alert.states']
            alert_states_ids = obj_alert_states.search(cr, uid, [('model_id', '=', model_id)], context=context)
            res = {'domain': {'state_id': [('id', 'in', alert_states_ids)]}}
        return res

    # value of 'state' for comparison
    def state_change(self, cr, uid, ids, state_id, context=None):
        obj_alert_states = self.pool['ir.alert.states']
        res_final = {'value': {}}
        if state_id:
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
        'date_comparison_field_id': fields.many2one('ir.model.fields', 'Comparison Date field',
                                                    domain="['&',('ttype', 'in', ('date','datetime')),('model_id', '=', model_id)]"),
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

    def _get_message(self, cr, uid, message, model_id, context):
        obj_fields = self.pool['ir.model.fields']
        obj_model = self.pool['ir.model']
        number = message.count('{')

        close_fields = message.count('}')
        if number != close_fields:
            raise orm.except_orm(_('Error'), _("missing curly brackets in alert message."))

        for counter in range(0, number):
            position_ini = message.find('{')
            position_fin = message.find('}')

            first_control = message[position_ini + 1: position_ini + 7]
            if first_control not in ('object'):
                string_in_error = message[position_ini - 1: position_fin + 1]
                raise orm.except_orm(_('Error'),
                                     _('Value not valid for ' + string_in_error + ". Valid value is 'object', for parent message (number record) or 'object.<name field>' for object field, in alert message."))

            if first_control == 'object':
                second_control = message[position_ini + 7: position_ini + 8]
                if second_control not in ('}', '.'):
                    string_in_error = message[position_ini - 1: position_fin + 1]
                    raise orm.except_orm(_('Error'),
                                         _('Value not valid for ' + string_in_error + ". Missing dot or '}' in alert message."))

            # obj_model_data = obj_model.read(cr, uid, vals['model_id'], ['model'], context=context)
            # examine_obj = self.pool.get(obj_model_data['model'])
            fields = (message[position_ini + 1: position_fin]).split('.')
            temp_id = model_id
            count_fields = 0
            total_fields = len(fields)
            for field in fields:
                count_fields += 1
                if field != 'object':
                    fields_ids = obj_fields.search(cr, uid, [('model_id', '=', temp_id), ('name', '=', field)])
                    if fields_ids:
                        fields_data = obj_fields.read(cr, uid, fields_ids[0], ['relation'], context=context)
                    else:
                        raise orm.except_orm(_('Error'), _('Value not valid for ' + message[
                                                                                    position_ini + 1: position_fin] + ". field not in object, in alert message."))
                    if fields_data['relation']:
                        temp_ids = obj_model.search(cr, uid, [('model', '=', fields_data['relation'])])
                        temp_id = temp_ids[0]
                    else:
                        if count_fields != total_fields:
                            raise orm.except_orm(_('Error'), _('Value not valid for ' + message[
                                                                                        position_ini + 1: position_fin] + ". field not in object, in alert message."))

            message = message[position_fin + 1:]
            return message

    def create(self, cr, uid, vals, context=None):
        obj_actions = self.pool.get('ir.actions.actions')

        # control message

        message = self._get_message(cr, uid, vals['message'], vals['model_id'], context)

        # control E-Mail message
        if ('flag_email' in vals) and (vals['flag_email']):
            message = self._get_message(cr, uid, vals['email_message'], vals['model_id'], context)

        # search actions id
        if ('is_parent' in vals) and (vals['is_parent']):
            actions_ids = obj_actions.search(cr, uid, [('name', '=', 'Family Alerts')])
            if actions_ids not in ([], False, ''):
                vals['action_id'] = actions_ids[0]
            else:
                if 'action_id' in vals:
                    del vals['action_id']

        return super(ir_alert_config, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        obj_actions = self.pool.get('ir.actions.actions')

        if 'model_id' in vals:
            temp_id = vals['model_id']
        else:
            obj_config = self.pool.get('ir.alert.config').read(cr, uid, ids[0], ['model_id'], context=context)
            temp_id = obj_config['model_id'][0]

        if 'message' in vals:
            # control message
            message = self._get_message(cr, uid, vals['message'], temp_id, context)

        if 'email_message' in vals:
            # control E-Mail message
            message = self._get_message(cr, uid, vals['email_message'], temp_id, context)

        # search actions id
        if ('is_parent' in vals) and (vals['is_parent']):
            actions_ids = obj_actions.search(cr, uid, [('name', '=', 'Family Alerts')])
            if actions_ids not in ([], False, ''):
                vals['action_id'] = actions_ids[0]
            else:
                if 'action_id' in vals:
                    del vals['action_id']

        return super(ir_alert_config, self).write(cr, uid, ids, vals, context=context)
