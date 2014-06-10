# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011-TODAY DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011-TODAY Didotech Inc. (<http://www.didotech.com>)
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

import time
from report import report_sxw
from osv import osv
import pooler
from tools.translate import _

class print_sim_location(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_sim_location, self).__init__(cr, uid, name, context=context)
        self.location_types = {}
        sim_location_ids = self.pool.get('res.sim.location').search(cr, uid, [], context=context)
        sim_locations = self.pool.get('res.sim.location').read(cr, uid, sim_location_ids, context=context)
        if sim_locations:
            for sim_loc in sim_locations:
                location = self.pool.get('ir.model').read(cr, uid, sim_loc['model'][0],['model'],context=context)['model']
                self.location_types.update({ location : sim_loc['name']})
        self.localcontext.update({
            'time': time,
            'get_sim_moves' : self.get_sim_moves,
            'get_location_name' : self.get_location_name,
            'get_location_type' : self.get_location_type,
        })

    def get_asset_moves(self,asset_id, start_date, end_date):
        result = []
        asset_moves_sql = """
            SELECT 
                id as move_id, 
                asset_id, 
                dest_location as location_id, 
                DATE(datetime) as start_date ,
                DATE((
                            select ni.datetime from asset_move_line as ni 
                            where ni.asset_id = asset_move_line.asset_id and ni.id > asset_move_line.id order by id limit 1
                         )) as end_date
                        
            FROM asset_move_line 
            where datetime between %s and %s and asset_id = %s
            union
            SELECT 
                pm.id as move_id, 
                pm.asset_id, 
                pm.dest_location as location_id, 
                DATE(pm.datetime) as start_date, 
                DATE((
                    select mi.datetime from asset_move_line as mi 
                    where mi.asset_id = pm.asset_id and mi.id > pm.id order by mi.id limit 1
                )) as end_date
            FROM asset_move_line pm
            inner join
                 (
                     SELECT asset_id, max(datetime) as datetime
                     FROM asset_move_line
                     where datetime < %s
                     group by asset_id
                 ) X
            on pm.asset_id = X.asset_id and pm.datetime = X.datetime
            and pm.asset_id = %s
            order by asset_id, move_id            
        """
        
        self.cr.execute(asset_moves_sql, (start_date, end_date , asset_id, start_date, asset_id))
        res = self.cr.fetchall()
        if res and  res[0][3] > start_date:
            if res[0][2] and 'asset.asset' in res[0][2]:
                asset_moves = self.get_asset_moves(asset_id, start_date, res[0][3] or end_date or time.strftime('%Y-%m-%d'))
                if not asset_moves:
                    result.append(['asset.asset,%s' % (asset_id), start_date, res[0][3]])
                else:
                    result += asset_moves
                
                asset_moves = self.get_asset_moves(asset_id, start_date, res[0][3] or end_date or time.strftime('%Y-%m-%d'))
                model_name, record_id = res[0][2].split(',')
                asset_moves = self.get_asset_moves(int(record_id), res[0][3], res[0][4] or end_date or time.strftime('%Y-%m-%d'))
                if not asset_moves:
                    result.append([res[0][2],res[0][3],res[0][4] or end_date])
                else:
                    result += asset_moves
            else:
                result.append(['asset.asset,%s' % (asset_id), start_date, res[0][3]])
                result.append([res[0][2], res[0][3], res[0][4]])
        if res and res[0][3] <= start_date:
            if res[0][2] and 'asset.asset' in res[0][2]:
                model_name, record_id = res[0][2].split(',')
                asset_moves = self.get_asset_moves(int(record_id), res[0][3], res[0][4] or end_date or time.strftime('%Y-%m-%d'))
                if not asset_moves:
                    result.append([res[0][2], start_date, res[0][4]])
                else:
                    result += asset_moves
            else:
                result.append([res[0][2], start_date, res[0][4]])
        for line in res[1:]:
            if line[2] and 'asset.asset' in line[2]:
                model_name,record_id = line[2].split(',')
                asset_moves = self.get_asset_moves(int(record_id), line[3], line[4] or end_date or time.strftime('%Y-%m-%d'))
                if not asset_moves:
                    result.append([line[2],line[3],line[4]])
                    continue
                result += asset_moves
            else:
                result.append([line[2],line[3],line[4]])
        return result
    def get_sim_moves(self,sim,form):
        move_lines = []
        sim_moves_sql = """
            SELECT id as move_id, sim_id, dest_location as location_id, DATE(datetime) as start_date ,DATE((
                select ni.datetime from res_sim_move_line as ni 
                where ni.sim_id = res_sim_move_line.sim_id and ni.id > res_sim_move_line.id order by id limit 1
             )) as end_date
             FROM res_sim_move_line 
             where datetime between %s and %s and sim_id = %s
             union
             SELECT pm.id as move_id, pm.sim_id, pm.dest_location as location_id, DATE(pm.datetime) as start_date, DATE((
                select mi.datetime from res_sim_move_line as mi 
                where mi.sim_id = pm.sim_id and mi.id > pm.id order by mi.id limit 1
             )) as end_date
             FROM res_sim_move_line pm
             inner join
             (
                     SELECT sim_id, max(datetime) as datetime
                     FROM res_sim_move_line
                     where datetime < %s
                     group by sim_id
             ) X
             on pm.sim_id = X.sim_id and pm.datetime = X.datetime
             and pm.sim_id = %s
             order by sim_id, move_id
        """
        
        self.cr.execute(sim_moves_sql, (form['start_date'], form['end_date'] , sim.id , form['start_date'], sim.id))
        res = self.cr.fetchall()
        for line in res:
            if line[2] and 'asset.asset' in line[2]:
                model_name,record_id = line[2].split(',')
                asset_moves = self.get_asset_moves(record_id,line[3],line[4] or form['end_date'] or time.strftime('%Y-%m-%d'))
                if not asset_moves:
                    move_lines.append([line[2],line[3],line[4]])
                    continue
                move_lines += asset_moves
            else:
                move_lines.append([line[2],line[3],line[4]])
        return move_lines
    def get_location_name(self,location):
        if location:
            model_name,record_id = location.split(',')
            pool = pooler.get_pool(self.cr.dbname)
            names = pool.get(model_name).name_get(self.cr, self.uid, [int(record_id)], context=self.localcontext)
            if names:
                return names[0][1]
        return False
    
    def get_location_type(self,location):
        if location:
            model_name,record_id = location.split(',')
            return self.location_types.get(model_name,model_name)
        return False
    
report_sxw.report_sxw('report.print.sim.location','res.sim','addons/hr_sim/report/print_sim_location.rml',parser=print_sim_location)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

