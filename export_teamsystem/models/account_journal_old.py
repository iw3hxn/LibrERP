# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016-2019 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import fields, orm


DIRECTIONS = [
    (0, 'Sinistra (0)'),
    (1, '1'),
    (2, '2')
]


class account_journal(orm.Model):
    _inherit = 'account.journal'
    _columns = {
        'teamsystem_code': fields.integer('Codice TeamSystem'),
        'teamsystem_invoice_position': fields.selection(DIRECTIONS, 'Posizione nella sequenza del numero')
    }

    # _sql_constraints = [('teamsystem_code', 'unique(code)', 'Codice TeamSystem deve essere univoco')]
