# -*- coding: utf-8 -*-
##############################################################################
#
#    by Bortolatto Ivan (ivan.bortolatto at didotech.com)
#    Copyright (C) 2013 Didotech Inc. (<http://www.didotech.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# from datetime import date

from openerp.osv import orm, fields


class IrAlertStates(orm.Model):

    _name = "ir.alert.states"
    _columns = {
        'model_id': fields.many2one('ir.model', 'Object'),
        'name': fields.char('State name', size=60),
        'value': fields.char('State value', size=60),
    }


