# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2013 Didotech srl (<http://www.didotech.com>). All Rights Reserved
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

from osv import osv
from tools.translate import _


class crm_meeting(osv.osv):
    _inherit = 'crm.meeting'
    
    def create(self, cr, uid, values, context=None):
        if values.get('user_id', False):
            if not uid == values['user_id']:
                employee_obj = self.pool.get('hr.employee')
                if not employee_obj.is_parent(cr, uid, values['user_id']):
                    raise osv.except_osv('Warning', _("You don't have rights to take appointment for this user"))
        else:
            values['user_id'] = uid
            
        return super(crm_meeting, self).create(cr, uid, values, context)
    
    def write(self, cr, uid, ids, values, context=None):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        
        employee_obj = self.pool.get('hr.employee')
        
        for event in self.browse(cr, uid, ids):
            if not event.user_id.id == uid and not employee_obj.is_parent(cr, uid, event.user_id.id):
                raise osv.except_osv('Warning', _("You don't have rights to change appointment for this user"))
            
            if values.get('user_id', False):
                if not uid == values['user_id']:
                    if not employee_obj.is_parent(cr, uid, values['user_id']):
                        raise osv.except_osv('Warning', _("You don't have rights to take appointment for this user"))
            
        return super(crm_meeting, self).write(cr, uid, ids, values, context)


class crm_phonecall(osv.osv):
    _inherit = 'crm.phonecall'
    
    def create(self, cr, uid, values, context=None):
        if values.get('user_id', False):
            if not uid == values['user_id']:
                employee_obj = self.pool.get('hr.employee')
                if not employee_obj.is_parent(cr, uid, values['user_id']):
                    raise osv.except_osv('Warning', _("You don't have rights to take appointment for this user"))
        else:
            values['user_id'] = uid
            
        return super(crm_phonecall, self).create(cr, uid, values, context)
    
    def write(self, cr, uid, ids, values, context=None):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        
        employee_obj = self.pool.get('hr.employee')
        
        for event in self.browse(cr, uid, ids):
            if not event.user_id.id == uid and not employee_obj.is_parent(cr, uid, event.user_id.id):
                raise osv.except_osv('Warning', _("You don't have rights to change appointment for this user"))
            
            if values.get('user_id', False):
                if not uid == values['user_id']:
                    if not employee_obj.is_parent(cr, uid, values['user_id']):
                        raise osv.except_osv('Warning', _("You don't have rights to take appointment for this user"))
            
        return super(crm_phonecall, self).write(cr, uid, ids, values, context)
