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


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    
    def is_parent(self, cr, uid, user_id):
        employee_ids = self.search(cr, uid, [('user_id', '=', user_id)])
        if employee_ids:
            employee = self.browse(cr, uid, employee_ids[0])
            parent_ids = self.search(cr, uid, [('user_id', '=', uid)])
            if parent_ids and employee.parent_id and employee.parent_id.id == parent_ids[0]:
                return True
            else:
                return False
        else:
            return False
