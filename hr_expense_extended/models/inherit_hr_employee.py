# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class hr_employee(orm.Model):
    _inherit = "hr.employee"
    
    def get_employee(self, cr, uid, user_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        employee_ids = self.search(cr, uid, [('user_id', '=', user_id)], context=context)
        if employee_ids:
            return self.browse(cr, uid, employee_ids[0], context)
        else:
            raise orm.except_orm('Error', _('No Employee is associated with this user'))

    _columns = {
        'vehicle': fields.char('Targa Veicolo')
    }
