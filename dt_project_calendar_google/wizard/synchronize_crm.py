# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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
from dateutil.tz import *
from dateutil.parser import *
from pytz import timezone
import pytz

from gdata import service
import gdata.calendar.service
import gdata.calendar
import atom

import wizard
import pooler
from osv import fields, osv
from tools.translate import _

_timezone_form =  '''<?xml version="1.0"?>
        <form string="This Wizard Synchronize CRM between OpenERP and Google Calendar">
        <separator string="Select Timezone" colspan="4"/>
        <field name="timezone_select"/>
        </form> '''

_timezone_fields = {
            'timezone_select': {
            'string': 'Time Zone',
            'type': 'selection',
            'selection': [(x, x) for x in pytz.all_timezones],
            'required': True,
            'default' : 'Europe/Rome'
        },
        }

class google_meeting_wizard(wizard.interface):

    calendar_service = ""

    def _add(self, calendar_service, username, title='',content='', where='', start_time=None, end_time=None):
        try:
            event = gdata.calendar.CalendarEventEntry()
            event.title = atom.Title(text=title)
            event.content = atom.Content(text=content)
            event.where.append(gdata.calendar.Where(value_string=where))
            time_format = "%Y-%m-%d %H:%M:%S"
            if start_time:
                # convert event start date into gmtime format
                timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))))
                starttime = time.strptime(timestring, time_format)
                start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', starttime)
            if end_time:
                # convert event end date into gmtime format
                timestring_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))))
                endtime = time.strptime(timestring_end, time_format)
                end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', endtime)
            if start_time is None:
              # Use current time for the start_time and have the event last 1 hour
              start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
              end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))
            event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
            cal_id = '/calendar/feeds/%s/private/full' %(username)
            new_event = calendar_service.InsertEvent(event, cal_id)
            return new_event
        except Exception, e:
            raise osv.except_osv('Error create !', e )

    def _synch_events(self, cr, uid, data, context={}):

        obj_user = pooler.get_pool(cr.dbname).get('res.users')
        google_auth_details = obj_user.browse(cr, uid, uid)
        obj_crm = pooler.get_pool(cr.dbname).get('project.task')
        if not google_auth_details.gmail_user or not google_auth_details.gmail_password or not google_auth_details.google_calendar:
            raise osv.except_osv('Warning !',
                                 'Please Enter google email id, google calendar id and password in users')
        if 'tz' in context and context['tz']:
            time_zone = context['tz']
        else:
            time_zone = data['form']['timezone_select']
        au_tz = timezone(str(time_zone))
        try :
            self.calendar_service = gdata.calendar.service.CalendarService()
            self.calendar_service.email = google_auth_details.gmail_user
            self.calendar_service.password = google_auth_details.gmail_password
            self.calendar_service.source = 'Tiny'
            self.calendar_service.max_results = 500 # to be check
            self.calendar_service.ProgrammaticLogin()
            # rajout code
            # recupere la date d'un mois plus tot
            date_ancien = datetime.date.today()-datetime.timedelta(31)
            date_mini = date_ancien.strftime("%Y-%m-%d")
            username = google_auth_details.google_calendar
            visibility = 'private'
            projection = 'full'
            query = gdata.calendar.service.CalendarEventQuery(username, visibility,projection)
            #pour limiter la requete chez Google à 1 mois d'ancienneté
            query.start_min = date_mini
            feed = self.calendar_service.CalendarQuery(query)
            ####
            tiny_events = obj_crm.search(cr, uid, [('user_id','=',uid),('date','>',date_mini)])
            if not google_auth_details.company_id.partner_id.address:
                raise wizard.except_wizard(_('Warning'), _('The Partner of the Main Company does not have any address defined!'))
            name = google_auth_details.company_id.partner_id.name
            city = google_auth_details.company_id.partner_id.address[0].city or ''
            street =  google_auth_details.company_id.partner_id.address[0].street or ''
            street2 = google_auth_details.company_id.partner_id.address[0].street2 or ''
            zip = google_auth_details.company_id.partner_id.address[0].zip or ''
            country = google_auth_details.company_id.partner_id.address[0].country_id.name or ''
            location2 = name +" "+street + " " +street2 + " " + city + " " + zip + " " + country
            tiny_events = obj_crm.browse(cr, uid, tiny_events)
            #feed = self.calendar_service.GetCalendarEventFeed()
            tiny_event_dict = {}
            for event in tiny_events:
                # ajoute nom du partenaire dans l'adresse
                location = location2
                if event.partner_id :
                  location = event.partner_id.name
                  if event.partner_id.city :
                        location = location + " "+ event.partner_id.city
                ###
                if not event.google_event_id:
                    new_event = self._add(self.calendar_service, username, event.name, event.description, location, event.date_start, event.date_end)
                    obj_crm.write(cr, uid, [event.id], {'google_event_id': new_event.id.text,
                       'event_modify_date': new_event.updated.text #should be correct!
                       })
                    tiny_event_dict[event.google_event_id] = event
                tiny_event_dict[event.google_event_id] = event
                #tiny_up = event.event_modify_date # Tiny google event modify date
            for i, an_event in enumerate(feed.entry):
                #print  an_event.updated.text, an_event.title.text
                google_id = an_event.id.text
                #print 'google_date: ',google_date
                if google_id in tiny_event_dict.keys():
                    event = tiny_event_dict[google_id]
                    google_up = an_event.updated.text # google event modify date
                    utime = dateutil.parser.parse(google_up)
                    au_dt = au_tz.normalize(utime.astimezone(au_tz))
                    timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                    google_up = timestring_update
                    #print 'google_up, tiny_up: ',google_up, tiny_up
                    if event.write_date > google_up:
                        # tiny events => google
                        an_event.title.text = event.name
                        an_event.content.text = event.description
                        an_event.where.insert(0, gdata.calendar.Where(value_string=location))
                        time_format = "%Y-%m-%d %H:%M:%S"
                        # convert event start date into gmtime format
                        timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(event.date_start, "%Y-%m-%d %H:%M:%S"))))
                        starttime = time.strptime(timestring, time_format)
                        start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', starttime)
                        start = (time.strptime(event.date, "%Y-%m-%d %H:%M:%S"))
                        # convert event end date into gmtime format
                        timestring_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(event.date_end, "%Y-%m-%d %H:%M:%S"))))
                        endtime = time.strptime(timestring_end, time_format)
                        end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', endtime)
                        if an_event.when:
                            an_event.when[0].start_time = start_time
                            an_event.when[0].end_time = end_time
                        update_event = self.calendar_service.UpdateEvent(an_event.GetEditLink().href, an_event)
                        
                    elif event.write_date < google_up:
                        # google events => tiny
                        utime = dateutil.parser.parse(an_event.updated.text)
                        au_dt = au_tz.normalize(utime.astimezone(au_tz))
                        timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                        name_event = an_event.title.text or ''
                        note_event = an_event.content.text or ''
                        if an_event.when:
                            stime = an_event.when[0].start_time
                            etime = an_event.when[0].end_time
                            stime = dateutil.parser.parse(stime)
                            etime = dateutil.parser.parse(etime)
                            try:
                                    # conversion temps universel
                                    #date de debut
                                    timestring = datetime.datetime(*stime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                                    local_dt = datetime.datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S")
                                    eur_dt = au_tz.localize(local_dt)
                                    timestring = pytz.utc.normalize(eur_dt.astimezone(pytz.utc)).strftime("%Y-%m-%d %H:%M:%S")
                                    #date de fin
                                    timestring_end = datetime.datetime(*etime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                                    local_dt = datetime.datetime.strptime(timestring_end, "%Y-%m-%d %H:%M:%S")
                                    eur_dt = au_tz.localize(local_dt)
                                    timestring_end = pytz.utc.normalize(eur_dt.astimezone(pytz.utc)).strftime("%Y-%m-%d %H:%M:%S")
                            except :
                                timestring = datetime.datetime(*stime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                                timestring_end = datetime.datetime(*etime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                            val = {
                               'name': name_event,
                               'description': note_event,
                               'date_start': timestring,
                               'date_end': timestring_end,
                               'event_modify_date': timestring_update
                               }
                            obj_crm.write(cr, uid, [event.id], val)

                    elif event.write_date == google_up:
                        pass

                else:
                    google_id = an_event.id.text
                    utime = dateutil.parser.parse(an_event.updated.text)
                    au_dt = au_tz.normalize(utime.astimezone(au_tz))
                    timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                    name_event = an_event.title.text or ''
                    note_event = an_event.content.text or ''
                    if an_event.when:
                        stime = an_event.when[0].start_time
                        etime = an_event.when[0].end_time
                        stime = dateutil.parser.parse(stime)
                        etime = dateutil.parser.parse(etime)
                        try :                             
                                    # conversion temps universel
                                    #date de debut
                                    timestring = datetime.datetime(*stime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                                    local_dt = datetime.datetime.strptime (timestring, "%Y-%m-%d %H:%M:%S")
                                    eur_dt = au_tz.localize(local_dt)
                                    timestring = pytz.utc.normalize(eur_dt.astimezone(pytz.utc)).strftime("%Y-%m-%d %H:%M:%S")
                                    #date de fin
                                    timestring_end = datetime.datetime(*etime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                                    local_dt = datetime.datetime.strptime (timestring_end, "%Y-%m-%d %H:%M:%S")
                                    eur_dt = au_tz.localize(local_dt)
                                    timestring_end = pytz.utc.normalize(eur_dt.astimezone(pytz.utc)).strftime("%Y-%m-%d %H:%M:%S")
                        except :
                                    timestring = datetime.datetime(*stime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                                    timestring_end = datetime.datetime(*etime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                        val = {
                           'name': name_event,
                           'description': note_event,
                           'date_start': timestring,
                           'date_end': timestring_end,
                           'user_id': google_auth_details.id,
                           'categ_id': 1,
                           'google_event_id': an_event.id.text,
                           'event_modify_date': timestring_update
                            }
                        obj_crm.create(cr, uid, val)

            return {}
        except Exception, e:
            if isinstance(e,wizard.except_wizard):
                raise osv.except_osv(e[0], e[1])
            raise osv.except_osv('Error except !', e )

    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _timezone_form, 'fields': _timezone_fields, 'state': [('synch', 'Synchronize')]}
        },

        'synch': {
            'actions': [_synch_events],
            'result': {'type': 'state', 'state': 'end'}
        }
    }

google_meeting_wizard('google.meeting.synch')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
