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

import base64
from osv import fields,osv
from tools.translate import _
import time
import datetime

class wizard_print_sim_location(osv.osv_memory):
    """
    Wizard to create custom report
    """
    _name = "wizard.print.sim.location"
    _description = "Create Report for Sim Locations"
    
    _columns = {
        'start_date' : fields.date('Start Date', required=True),
        'end_date' : fields.date('End Date', required=True),
    }
    
    _defaults = { 
        'start_date' : lambda *a: time.strftime('%Y-%m-%d'),
        'end_date' : lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def print_sim_locations(self, cr, uid, ids, context={}):
        if context is None:
            context = {}
        datas = {'ids' : context.get('active_ids',[])}
        res = self.read(cr, uid, ids, ['start_date','end_date'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'print.sim.location',
            'datas': datas,
       }
wizard_print_sim_location()
