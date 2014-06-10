# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Didotech srl (info at didotech.com)
#
#                          All Rights Reserved.
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

from osv import fields, osv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from tools.translate import _
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


#
## This class contains the project calendar object and the copy of external object
#
class project_task(osv.osv):
    _inherit = "project.task"

    _columns = {
        'model_name': fields.char(_('Type'), size=50, readonly=True),
        'model_id': fields.integer(_('Original id')),
        'event_write_date': fields.datetime('Last sync', readonly=True, help='Original event modify date'),
        'location': fields.char(_('Location'), size=50, readonly=True),
        #'attendee': fields.char(_('Attendee'), size=50, readonly=True),
        ## May be this fields can be usefull also:
        #!'attendee_ids': fields.many2many('project.task.attendee', string='Attendees', states={'done': [('readonly', True)]}),
        #!'mail': fields.char('Mail', size=50, readonly=True),
    }
      
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'model_name': 'project.task',
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        
        config_obj = self.pool.get('project.calendar.conf.information')
        for task in self.browse(cr, uid, ids, context=context):
            config_ids = config_obj.search(cr, uid, [('model', '=', task.model_name)])
            if config_ids:
                value = {}
                
                config = config_obj.browse(cr, uid, config_ids[0])
                
                # Perform field mapping as defined in config
                for field in ('name', 'description', 'responsible', 'date_start', 'date_end', 'planned_hours', 'location'):
                    if vals.get(field, False) and getattr(config, field).name:
                        value[getattr(config, field).name] = vals[field]
                
                if value:
                    # TODO: If this script is called together with Google meeting Concurrency writing problem can happen:
                    self.pool.get(task.model_name).write(cr, uid, task.model_id, value)
        
        return super(project_task, self).write(cr, uid, ids, vals, context=context)
   
    ## Method to check the original object
    def check_original_object(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        obj = self.browse(cr, uid, ids[0], context=context)
         
        return {
            'name': 'Edit original object',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': None,
            'res_model': obj.model_name,
            'res_id': obj.model_id,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'context': context,
        }

    ## Method for updating the project calendar with new object
    def sync_events(self, cr, uid, context=None):
        calendar_conf_info_obj = self.pool.get('project.calendar.conf.information')
        calendar_conf_ids = calendar_conf_info_obj.search(cr, uid, [('model', '!=', None)])
        config_infos = calendar_conf_info_obj.browse(cr, uid, calendar_conf_ids)
        
        #calculation period to synchronize
        config_obj = self.pool.get('project.calendar.conf')
        config_ids = config_obj.search(cr, uid, [])
        for config in config_obj.browse(cr, uid, config_ids):
            date_now = datetime.now()
            date_before = date_now + relativedelta(months=-config.periode_start)
            date_after = date_now + relativedelta(months=+config.periode_end)
               
            for config_info in config_infos:
                model_obj = self.pool.get(config_info.model.model)
                event_ids = model_obj.search(cr, uid, [(config_info.date_start.name, '>=', date_before.strftime('%Y-%m-%d %H:%M:%S')), (config_info.date_start.name, '<=', date_after.strftime('%Y-%m-%d %H:%M:%S'))])
                events = model_obj.browse(cr, uid, event_ids)
                
                for event in events:
                    new_vals = {}
                    
                    results = self.pool.get(config_info.model.model).read(cr, uid, event.id, [
                        config_info.name.name,
                        config_info.description.name,
                        config_info.user_id.name,
                        config_info.date_start.name,
                        config_info.date_end.name,
                        config_info.date_deadline.name,
                        config_info.planned_hours.name,
                        config_info.location.name,
                        #config_info.attendee.name,
                        #config_info.mail.name
                    ])
                    
                    if config_info.name.name:
                        new_vals['name'] = results[config_info.name.name]
                    if config_info.description.name:
                        new_vals['description'] = results[config_info.description.name]
                    if config_info.user_id.name:
                        new_vals['user_id'] = results[config_info.user_id.name][0]
                    if config_info.date_start.name:
                        new_vals['date_start'] = results[config_info.date_start.name]
                    if config_info.date_end.name:
                        new_vals['date_end'] = results[config_info.date_end.name]
                    if config_info.date_deadline.name:
                        new_vals['date_deadline'] = results[config_info.date_deadline.name]
                    if config_info.planned_hours.name:
                        new_vals['planned_hours'] = results[config_info.planned_hours.name]
                    if config_info.location.name:
                        new_vals['location'] = results[config_info.location.name]
                    #if config_info.attendee.name:
                    #    new_vals['attendee'] = results[config_info.attendee.name]
                    #if config_info.mail.name:
                    #    new_vals['mail'] = results[config_info.mail.name]
                    
                    if not new_vals.get('date_deadline', False) and new_vals['date_start']:
                        new_vals['date_deadline'] = new_vals['date_start']
                        
                    if not new_vals.get('date_end', False) and new_vals['date_start'] and new_vals['planned_hours']:
                        date_start = datetime.strptime(new_vals['date_start'], '%Y-%m-%d %H:%M:%S')
                        planned_hours = int(new_vals['planned_hours'])
                        date_end = date_start + relativedelta(hours=+planned_hours)
                        new_vals['date_end'] = date_end.strftime('%Y-%m-%d %H:%M:%S')
                    
                    if new_vals:
                        if "-" in str(event.id):
                            event_id = str(event.id).split('-')[0]
                        else:
                            event_id = event.id
                        
                        task_ids = self.search(cr, uid, [('model_id', '=', event_id), ('model_name', '=', config_info.model.model)])
                        perms = model_obj.perm_read(cr, uid, [event_id])
                        new_vals['event_write_date'] = perms[0].get('write_date', False)

                        if task_ids:
                            for task in self.browse(cr, uid, task_ids):
                                if not new_vals['event_write_date'] == task.event_write_date:
                                    super(project_task, self).write(cr, uid, task_ids, new_vals, context=context)
                                    if event.state == 'done':
                                        #if config.delete_done:
                                        #   calendar_obj.unlink(cr, uid, project_task_ids)
                                        
                                        # We should do_close() after write(),
                                        # because date_end should be written first
                                        self.do_close(cr, uid, task_ids)
                                        ## do_close() writes to task_obj, so model_obj also will have a new write time
                                        perms = model_obj.perm_read(cr, uid, [event_id])
                                        super(project_task, self).write(cr, uid, task_ids, {'event_write_date': perms[0].get('write_date', False)}, context=context)
                                    
                        else:
                            #if not (task.state == 'done' and config.delete_done):
                            if not event.state == 'done':
                                new_vals['model_id'] = event_id
                                new_vals['model_name'] = config_info.model.model
                                self.create(cr, uid, new_vals, context=None)
                    else:
                        _logger.error(u"+++ This is impossible condition +++")
        
        return True


#
## This class contains the configuration information
#
class project_calendar_conf(osv.osv):
    _name = "project.calendar.conf"
    _description = "Capacity Planning"
    
    ## Call of button configuration
    #  @param self The object pointer.
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    #
    def check_update_calendar(self, cr, uid, ids, context=None):
        #return self.check_cron(cr, uid, 'project.calendar.conf')
        return self.pool.get('project.task').sync_events(cr, uid)
    
    _columns = {
        'name': fields.char('Name', size=30, required=True, help=_("The name of the configuration.")),
        'conf_info': fields.one2many('project.calendar.conf.information', 'conf_id', 'conf info'),
        'cron': fields.many2one('ir.cron', _('Cron'), required=True, ondelete='cascade'),
        'periode_start': fields.integer(_('Before')),
        'periode_end': fields.integer(_('After')),
        #'delete_done': fields.boolean(_('Remove finished tasks'))
    }
    
    _defaults = {
        'periode_start': 1,
        'periode_end': 3,
        #'delete_done': True,
    }
    
    ## Method for cleaning the project calendar
    #  @param self The object pointer.
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language

    def clean_project_calendar(self, cr, uid, ids, context=None):
        #calendar_obj = self.pool.get('project.calendar')
        #calendar_ids = calendar_obj.search(cr, uid, [('model_name', '!=', 'project calendar')])
        #calendar_obj.unlink(cr, uid, calendar_ids)
        
        return True
    
    ## Method for clean the configuration of project calendar
    #  @param self The object pointer.
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    #
    def clean_project_calendar_conf(self, cr, uid, ids, context=None):
        calendar_obj = self.pool.get('project.calendar.conf.information')
        calendar_ids = calendar_obj.search(cr, uid, [])
        calendar_obj.unlink(cr, uid, calendar_ids)

        return True
    
    ## Surcharge of unlink method for delete information configuration when the configuration is delete
    #  @param self The object pointer.
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param delall optional parameter
    #
    def unlink(self, cr, uid, ids, delall=None, *args, **kwargs):
        o_obj = self.pool.get('project.calendar.conf.information')
        o_ids = o_obj.search(cr, uid, [])
        o_obj.unlink(cr, uid, o_ids)
        
        return super(project_calendar_conf, self).unlink(cr, uid, ids, *args, **kwargs)

    ## Surcharge of create method to verify existence of the configuration
    #  @param self The object pointer.
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param vals The dictionary of field values to update
    #  @param context The optional dictionary of contextual parameters such as user language
    #
    def create(self, cr, uid, vals, context=None):
        obj_ids = self.pool.get('project.calendar.conf').search(cr, uid, [])
        if obj_ids:
            raise osv.except_osv('Error!', 'The configuration already exists.')
        
        return super(project_calendar_conf, self).create(cr, uid, vals, context=context)


#
## This class contains different types of objects that will be synchronized in the calendar
#
class project_calendar_conf_information(osv.osv):
    _name = "project.calendar.conf.information"
    _description = "Information"

    _columns = {
        'conf_id': fields.many2one('project.calendar.conf', _('Configuration'), readonly=True, invisible=True),
        #'model': fields.many2one('ir.model', _('Object'), required=True, domain="[('model', 'in', ('crm.meeting', 'crm.phonecall', 'project.task', 'project.issue', 'crm.case.stage', 'hr.holidays'))]"),
        'model': fields.many2one('ir.model', _('Object'), required=True, domain="[('model', 'in', ('crm.meeting', 'crm.phonecall'))]"),
        'name': fields.many2one('ir.model.fields', _('Name'), domain="['&',('ttype', '=', 'char'), ('model_id', '=', model)]", required=True),
        'description': fields.many2one('ir.model.fields', _('Description'), domain="['&', ('ttype', '=', ['char', 'text']), ('model_id', '=', model)]"),
        'user_id': fields.many2one('ir.model.fields', _('Responsible'), domain="['&', ('ttype', '=', 'many2one'), ('model_id', '=', model)]"),
        'date_start': fields.many2one('ir.model.fields', _('Start date'), required=True, domain="['&', ('ttype', '=', 'datetime'), ('model_id', '=', model)]"),
        'date_deadline': fields.many2one('ir.model.fields', _('Deadline'), domain="['&',('ttype', '=', 'datetime'), ('model_id', '=', model)]"),
        'date_end': fields.many2one('ir.model.fields', _('End date'), domain="['&',('ttype', '=', 'datetime'), ('model_id', '=', model)]"),
        'planned_hours': fields.many2one('ir.model.fields', _('Duration'), domain="['&',('ttype', '=', 'float'), ('model_id', '=', model)]"),
        'location': fields.many2one('ir.model.fields', _('Location'), domain="['&',('ttype', '=', 'char'), ('model_id', '=', model)]"),
        'attendee': fields.many2one('ir.model.fields', _('Attendee'), domain="['&',('ttype', '=', 'char'), ('model_id', '=', model)]"),
        'mail': fields.many2one('ir.model.fields', 'Mail', domain="['&', ('ttype', '=', 'char'), ('model_id', '=', model)]"),
    }
    
    def on_change_object(self, cr, uid, ids, model_id, context=None):
        if not model_id:
            return False
        
        model = self.pool.get('ir.model').browse(cr, uid, model_id, context=context).model
        
        value = {
            'date_end': None,
            'location': None,
            'mail': None,
            'planned_hours': None,
        }
        
        field_map = {
            'name': 'name',
            'user_id': 'user_id',
            'description': 'description',
            'date_start': 'date_start',
            'date_end': 'date_end',
            #'create_date': 'date_start',
            'date_from': 'date_start',
            'date_to': 'date_end',
            'date': 'date_start',
            'date_deadline': 'date_deadline',
            'location': 'location',
            'email_from': 'mail',
            'duration': 'planned_hours',
            'planned_hours': 'planned_hours',
        }
        
        model_field_map = {
            #'project.task': ['date_start', 'date_end', 'planned_hours'],
            #'project.issue': ['create_date', ],  # da testare
            #'crm.case.stage': ['create_date', ],
            #'hr.holidays': ['date_from', 'date_to'],  # da testare
            'crm.meeting': ['location', 'email_from', 'duration', 'date', 'date_deadline'],
            'crm.phonecall': ['duration', 'date'],
        }
        
        for field in ('name', 'user_id', 'description'):
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model", "=", model), ("name", "=", field)])
            if ids_field:
                value[field_map[field]] = ids_field[0]
        
        for field in model_field_map[model]:
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model", "=", model), ("name", "=", field)])
            if ids_field:
                value[field_map[field]] = ids_field[0]
        
        return {'value': value}
