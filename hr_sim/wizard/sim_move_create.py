# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 DeneroTeam. (<http://www.deneroteam.com>)
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
##############################################################################

from osv import fields, osv
from tools.translate import _
import time
from hr_sim.res_sim import _get_location


class sim_move_create(osv.osv_memory):
    _name = "sim.move.create"
    _description = "Move Sim"
    _columns = {
            "description": fields.char('Comment/Reason', size=64, required=True,),
            "dest_location": fields.reference("Destination Location", selection = _get_location, size=128),
            "user_id": fields.many2one("res.users","Moved By",required=True),
            "move_date": fields.datetime("Move Date", required=True),
            'sim_use_id': fields.many2one('res.sim.use', 'Utilizzo'),
            'sim_ids': fields.many2many('res.sim', 'res_sim_allocation_hr_sim_rel', 'move_id', 'sim_id', "SIMs"),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(sim_move_create, self).default_get(cr, uid, fields, context=context)
        
        if context['active_model'] == 'res.sim':
            sim_ids = context and context.get('active_ids', []) or []
        else:
            sim_ids = []
            
        locations = [model for model, description in _get_location(self, cr, uid)]
        if context['active_model'] in locations:
            active_ids = context.get('active_ids', []) or []
            if active_ids:
                dest_location = context['active_model'] + ',' + str(active_ids[0])
            else:
                dest_location = False
        else:
            dest_location = False
        
        res.update({
            'sim_ids': sim_ids,
            'move_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'dest_location': dest_location,
        })
        return res
    
    def sim_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context_id = context and context.get('active_id', False) or False
        #sim_ids = context and context.get('active_ids',[]) or []
        obj_sim = self.pool.get('res.sim')
        obj_move = self.pool.get('res.sim.allocation')
        move_line_obj = self.pool.get('res.sim.move.line')
        
        for data in self.read(cr, uid, ids, context=context):
            sim_lines = []
            dest_location = data['dest_location'] or False
            sim_ids = data.get('sim_ids', []) or []
            sim_use_id = data.get('sim_use_id', False)
            for sim in obj_sim.read(cr, uid, sim_ids, ['location', 'sim_internal_number']):
                if sim and not sim['location'] == data['dest_location']:
                    if not sim['location'] or not dest_location:
                        move_line_id = move_line_obj.create(cr, uid, {
                            'description': data['description'] or "NO-COMMENT",
                            'sim_id': sim['id'],
                            'source_location': sim['location'] or False,
                            'dest_location': dest_location,
                            'datetime': data['move_date'],
                            'user_id': data['user_id'][0],
                        })
                        if move_line_id:
                            sim_lines.append(move_line_id)
                    else:
                        raise osv.except_osv(_('Warning!'), _("SIM [{sim}] should be moved to warehouse first.".format(sim=sim['sim_internal_number'])))
            
            if sim_lines:
                move_id = obj_move.create(cr, uid, {
                    'name' : data['description'] or "NO-COMMENT",
                    'datetime': data['move_date'],
                    'dest_location' : dest_location,
                    'sim_move_lines' : [(6, 0, sim_lines)],
                    'user_id': data['user_id'][0],
                })
                if move_id:
                    sim_update = {'location': dest_location}
                    if sim_use_id:
                        sim_update['sim_use_id'] = sim_use_id
                    obj_sim.write(cr, uid, sim_ids, sim_update)
                    
        return {'type': 'ir.actions.act_window_close'}
    
    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }
    
sim_move_create()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
