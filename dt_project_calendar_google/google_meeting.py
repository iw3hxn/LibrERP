# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (C) 2013-2014 Didotech srl (<http://www.didotech.com>). All Rights Reserved
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

import time
import datetime
import dateutil
from pytz import timezone
import pytz
import gdata.calendar.service
import gdata.calendar
import atom
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class res_users(orm.Model):
    _inherit = "res.users"
    _description = 'res.users'

    _columns = {
        'google_calendar': fields.char('Google Calendar Id', size=128),
        'google_timezone': fields.selection([(x, x) for x in pytz.all_timezones], 'Google timezone'),
        'google_auto': fields.boolean('Synchro Scheduler', help='check this for automatic synchro')
    }
    
    _defaults = {
        'google_calendar': lambda *a: 'default',
        'google_timezone': lambda *a: 'Europe/Rome'
    }


class project_task(orm.Model):
    _inherit = "project.task"
    _description = "case"
    
    def _get_date(self, cr, uid, ids, field_name, arg, context):
        result = {}
        perms = self.perm_read(cr, uid, ids)
        for perm in perms:
            result[perm['id']] = {
                'date_write': perm.get('write_date', False),
                'date_create': perm.get('create_date', False),
            }
        return result

    _columns = {
        'google_event_id': fields.char('Google Event Id', size=512, readonly=True),
        'event_modify_date': fields.datetime('Google Modify Date', readonly=True, help='google event modify date'),
        'date_write': fields.function(_get_date, string='Write date', method=True, type='datetime', multi=True),
        'date_create': fields.function(_get_date, string='Create date', method=True, type='datetime', multi=True),
    }
    
    _sql_constraints = [
        ('google_event_id_uniq', 'unique(google_event_id)', 'Google Event Id must be unique!')
    ]

    def _add(self, calendar_service, username, title='', content='', where='', start_time=None, end_time=None):
        try:
            event = gdata.calendar.CalendarEventEntry()
            event.title = atom.Title(text=title)
            event.content = atom.Content(text=content)
            event.where.append(gdata.calendar.Where(value_string=where))
            
            if start_time:
                # convert event start date into gmtime format
                start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.mktime(time.strptime(start_time, DEFAULT_SERVER_DATETIME_FORMAT))))
            if end_time:
                # convert event end date into gmtime format
                end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.mktime(time.strptime(end_time, DEFAULT_SERVER_DATETIME_FORMAT))))
            else:
                end_time = start_time
            #if start_time is None:
            #   Use current time for the start_time and have the event last 1 hour
            #  start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
            #  end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))
            event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
            cal_id = '/calendar/feeds/%s/private/full' % (username)
            new_event = calendar_service.InsertEvent(event, cal_id)
            return new_event
        except Exception, e:
            print e
            return False
        
    def location(self, task):
        if task.model_name and task.model_name == 'crm.phonecall':
            return _('Phonecall')
        elif task.model_name and task.model_name == 'crm.meeting':
            if task.partner_id:
                return "{name} {street} {street2} {city} {zip_code} {country}".format(
                    name=task.user_id.company_id.partner_id.name,
                    street=task.user_id.company_id.partner_id.address[0].street or '',
                    street2=task.user_id.company_id.partner_id.address[0].street2 or '',
                    city=task.user_id.company_id.partner_id.address[0].city or '',
                    zip_code=task.user_id.company_id.partner_id.address[0].zip or '',
                    country=task.user_id.company_id.partner_id.address[0].country_id.name or ''
                )
            else:
                return task.user_id.company_id.partner_id.name
        else:
            return ''
            
    def synchro_scheduler(self, cr, uid, ids=False, context=None):
        user_obj = self.pool['res.users']
        user_ids = user_obj.search(cr, uid, [])
        
        for user in user_obj.browse(cr, uid, user_ids):
            #print 'nome: ', user.name
            if user.google_auto and user.gmail_user and user.gmail_password and user.google_calendar:
                if isinstance(context, dict) and context.get('tz', False):
                    time_zone = context['tz']
                else:
                    time_zone = user.google_timezone
                au_tz = timezone(str(time_zone))
                
                try:
                    self.calendar_service = gdata.calendar.service.CalendarService()
                    self.calendar_service.email = user.gmail_user
                    self.calendar_service.password = user.gmail_password
                    self.calendar_service.source = 'Tiny'
                    self.calendar_service.max_results = 500  # to be check
                    self.calendar_service.ProgrammaticLogin()
                    # rajout code
                    # recupere la date d'un mois plus tot
                    date_from = datetime.date.today() - datetime.timedelta(31)
                    date_mini = date_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    username = user.google_calendar
                    visibility = 'private'
                    projection = 'full'
                    query = gdata.calendar.service.CalendarEventQuery(username, visibility, projection)
                    #pour limiter la requete chez Google à 1 mois d'ancienneté
                    query.start_min = date_mini
                    feed = self.calendar_service.CalendarQuery(query)
                    ####
                    event_ids = self.search(cr, uid, [('user_id', '=', user.id), ('date_start', '>', date_mini)])

                    if user.company_id.partner_id.address:
                        event_dict = {}
                        
                        events = self.browse(cr, uid, event_ids)
                        #feed = self.calendar_service.GetCalendarEventFeed()
                        for event in events:
                            location = self.location(event)
                            #print 'Location: ', location
                            if event.google_event_id:
                                event_dict[event.google_event_id] = event
                            else:
                                ## Add from OpenERP => Google:
                                if event.date_end:
                                    date_end = event.date_end
                                else:
                                    date_end = event.date_start
                                
                                new_event = self._add(self.calendar_service, username, event.name, event.description, location, event.date_start, date_end)
                                if new_event:
                                    self.write(cr, uid, [event.id], {
                                        'google_event_id': new_event.id.text,
                                        'event_modify_date': new_event.updated.text  # should be correct!
                                    })
                                    event_dict[new_event.id.text] = event
                        
                        for i, an_event in enumerate(feed.entry):
                            google_id = an_event.id.text
                            if google_id in event_dict:
                                event = event_dict[google_id]
                                google_up = an_event.updated.text  # google event modify date
                                utime = dateutil.parser.parse(google_up)
                                au_dt = au_tz.normalize(utime.astimezone(au_tz))
                                timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                google_up = timestring_update
                                
                                #perms = self.perm_read(cr, uid, [event.id])
                                #event_write_date = perms[0].get('write_date', False)
                                #if event_write_date:
                                #    event_write_date = event_write_date.split('.')[0]
                                event_write_date = event.event_modify_date

                                if event_write_date > google_up:
                                    # OpenERP events => google
                                    an_event.title.text = event.name
                                    an_event.content.text = event.description
                                    an_event.where.insert(0, gdata.calendar.Where(value_string=location))
                                    
                                    # convert event start date into gmtime format
                                    start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.mktime(time.strptime(event.date_start, DEFAULT_SERVER_DATETIME_FORMAT))))
                                    
                                    # convert event end date into gmtime format
                                    end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.mktime(time.strptime(event.date_end, DEFAULT_SERVER_DATETIME_FORMAT))))
                                    
                                    if an_event.when:
                                        an_event.when[0].start_time = start_time
                                        an_event.when[0].end_time = end_time
                                    self.calendar_service.UpdateEvent(an_event.GetEditLink().href, an_event)
                                    
                                elif event_write_date < google_up:
                                    # google events => OpenERP
                                    utime = dateutil.parser.parse(an_event.updated.text)
                                    au_dt = au_tz.normalize(utime.astimezone(au_tz))
                                    timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                    name_event = an_event.title.text or ''
                                    note_event = an_event.content.text or ''
                                    location = an_event.where[0].value_string or ''
                                    #print 'Google : ', name_event, ' in ', location
                                    if an_event.when:
                                        stime = an_event.when[0].start_time
                                        stime = dateutil.parser.parse(stime)
                                        
                                        etime = an_event.when[0].end_time
                                        etime = dateutil.parser.parse(etime)
                                        
                                        try:
                                            # Trasform local to european time
                                            eur_dt = au_tz.localize(datetime.datetime(*stime.timetuple()[:6]))
                                            date_start = pytz.utc.normalize(eur_dt.astimezone(pytz.utc))
                                            
                                            # Trasform local to european time
                                            eur_dt = au_tz.localize(datetime.datetime(*etime.timetuple()[:6]))
                                            date_end = pytz.utc.normalize(eur_dt.astimezone(pytz.utc))
                                        except:
                                            date_start = datetime.datetime(*stime.timetuple()[:6])
                                            date_end = datetime.datetime(*etime.timetuple()[:6])
                                        
                                        duration = date_end - date_start
                                        
                                        val = {
                                            'name': name_event,
                                            'description': note_event,
                                            'date_start': date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                            'date_deadline': date_start.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                            'date_end': date_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                            'planned_hours': duration.seconds / 3600.00,
                                            'location': location,
                                            'event_modify_date': timestring_update
                                        }
                                        self.write(cr, uid, [event.id], val)
            
                                elif event_write_date == google_up:
                                    pass
    
                            else:
                                utime = dateutil.parser.parse(an_event.updated.text)
                                au_dt = au_tz.normalize(utime.astimezone(au_tz))
                                timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                name_event = an_event.title.text or ''
                                note_event = an_event.content.text or ''
                                location = an_event.where[0].value_string or ''
                                #print 'New Google : ', name_event, ' in ', location
                                
                                if an_event.when:
                                    stime = an_event.when[0].start_time
                                    etime = an_event.when[0].end_time
                                    stime = dateutil.parser.parse(stime)
                                    etime = dateutil.parser.parse(etime)
                                    try:
                                        eur_dt = au_tz.localize(datetime.datetime(*stime.timetuple()[:6]))
                                        date_start = pytz.utc.normalize(eur_dt.astimezone(pytz.utc))
                                        
                                        eur_dt = au_tz.localize(datetime.datetime(*etime.timetuple()[:6]))
                                        date_end = pytz.utc.normalize(eur_dt.astimezone(pytz.utc))
                                    except:
                                        date_start = datetime.datetime(*stime.timetuple()[:6])
                                        date_end = datetime.datetime(*etime.timetuple()[:6])
                                        
                                    duration = date_end - date_start
                                    
                                    if date_from >= datetime.date(date_start.year, date_start.month, date_start.day):
                                        # This happens when event lasts for few days
                                        old_event_ids = self.search(cr, uid, [('google_event_id', '=', google_id)])
                                    else:
                                        old_event_ids = False
                                    
                                    if not old_event_ids:
                                        self.create(cr, uid, {
                                            'name': name_event,
                                            'description': note_event,
                                            'date_start': date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                            'date_deadline': date_start.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                            'date_end': date_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                            'planned_hours': duration.seconds / 3600.00,
                                            'user_id': user.id,
                                            #'categ_id': 1,
                                            'location': location,
                                            'google_event_id': an_event.id.text,
                                            'event_modify_date': timestring_update
                                        })
                    else:
                        continue
                    
                except Exception, e:
                    print e
                    continue

        return True
