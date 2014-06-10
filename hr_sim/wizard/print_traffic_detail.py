# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################.

import base64
from osv import fields,osv
from tools.translate import _
import time
import datetime

delimiter = ';'
#delimiter = '\t'


class wizard_print_traffic_detail(osv.osv_memory):
    """
    Wizard to create custom report
    """
    _name = "wizard.print.traffic.detail"
    _description = "Create Report"
    
    _columns = {
        'start_date' : fields.date('Start Date', required=True),
        'end_date' : fields.date('End Date', required=True),
        'data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 16, readonly=True),
        'state': fields.selection((
            ('choose','choose'),   # choose date
            ('get','get'),         # get the file
        )),
    }
    
    _defaults = { 
        'state': lambda *a: 'choose',
        'start_date' : lambda *a: time.strftime('%Y-%m-%d'),
        'end_date' : lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def format_time(self, seconds):
        duration = {'hours': 0, 'minutes': 0, 'seconds': 0}
        duration['hours'] = seconds / 3600
        duration['minutes'] = (seconds - duration['hours'] * 3600) / 60
        duration['seconds'] = seconds - duration['hours'] * 3600 - duration['minutes'] * 60
        return '{hours:02}:{minutes:02}:{seconds:02}'.format(hours=duration['hours'], minutes=duration['minutes'], seconds=duration['seconds'])
    
    def print_traffic_detail(self, cr, uid, ids, context={}):
        this = self.browse(cr, uid, ids)[0]
        
        for sim_id in context['active_ids']:
            phone_number = self.pool.get('res.sim').browse(cr, uid, context['active_ids'][0])
                        
            file_name = '{0}_{1.start_date}_{1.end_date}.csv'.format(phone_number.imei, this)
            
            output = 'From {0}{1}To {2}\n\n'.format(this.start_date, delimiter, this.end_date)
            output += 'Numero primario: {0.prefix_number}{0.number}\n'.format(phone_number)
            fields = ['call_type', 'description', 'dest_number', 'call_date', 'duration', 'data_packets', 'amount', 'contract']
        
            call_ids = self.pool.get('res.sim.traffic').search(cr, uid, [('sim_id', '=', sim_id), ('call_date', '>=', this.start_date), ('call_date', '<=', this.end_date)], order='call_date')
            export_file = self.pool.get('res.sim.traffic').export_data(cr, uid, call_ids, fields, context)
            
            fields = [field.capitalize() for field in fields]
            output += delimiter.join(fields) + '\n'        
            for row in export_file['datas']:
                print row
                if row[4]:
                    row[4] = self.format_time(int(row[4]))
                    
                new_row = []
                for field in row:
                    if not field:
                        field = ''
                    new_row.append(field)
                new_row[-2] = new_row[-2].replace('.', ',')
                output += delimiter.join(new_row) + '\n'
                #print output
            
            generic_call_count, generic_duration, data_packets, generic_traffic = self.get_total(cr, sim_id, this.start_date, this.end_date, call_type='generic')
            data_call_count, data_duration, data_packets, data_traffic = self.get_total(cr, sim_id, this.start_date, this.end_date, call_type='data')
            call_count, duration, total_data_packets, total_traffic = self.get_total(cr, sim_id, this.start_date, this.end_date, call_type='all')
            
            if generic_traffic:
                output += 'Numero totale chiamate generiche: {0}{1}\n'.format(delimiter, generic_call_count)
                output += 'Totale durata traffico generico utenza: {0}{1}\n'.format(delimiter, generic_duration)
                output += 'Totale importo traffico generico utenza: {0}{1}\n'.format(delimiter, generic_traffic)
            
            if data_traffic:
                output += 'Numero totale chiamate dati: {0}{1}\n'.format(delimiter, data_call_count)
                output += 'Totale durata traffico dati utenza: {0}{1}\n'.format(delimiter, data_duration)
                output += 'Totale pacchetti dati utenza: {0}{1}\n'.format(delimiter, data_packets)
                output += 'Totale importo traffico dati utenza: {0}{1}\n'.format(delimiter, data_traffic)
            
            output += 'Numero totale chiamate: {0}{1}\n'.format(delimiter, call_count)
            output += 'Durata Totale chiamate: {0}{1}\n'.format(delimiter, duration)
            output += 'Totale traffico utenza: {0}{1}\n'.format(delimiter, total_traffic)
            

        out=base64.encodestring(output)
        return self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': file_name}, context=context)
    
    def get_total(self, cr, sim_id, start_date, end_date, call_type='all'):
        call_count = 1
        total_calls_duration = 1
        total_calls_traffic = 1
        total_traffic = 1
        duration = '00:00:00'
        
        query = """SELECT COUNT(*), SUM(duration), SUM(data_packets), SUM(amount)
            FROM res_sim_traffic 
            WHERE sim_id = {0}
            AND call_date >= '{1}'
            AND call_date <= '{2} 23:59:59'""".format(sim_id, start_date, end_date)
        
        if call_type == 'generic':
            query += ' AND data_packets IS NULL'
        elif call_type == 'data':
            query += ' AND data_packets IS NOT NULL'
        
        cr.execute(query)
        calls = cr.fetchall()
        if calls:
            call_count, calls_duration, data_packets, total_traffic = calls[0]        
        
        if calls_duration:
            duration = self.format_time(calls_duration)
            
        total_traffic = str(total_traffic).replace('.', ',')
        return call_count, duration, data_packets, total_traffic
        
wizard_print_traffic_detail()
