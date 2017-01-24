# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp (<http://www.camptocamp.at>)
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
from openerp.osv import orm, fields


class ir_sequence_installer(orm.TransientModel):
    _name = 'ir.sequence.installer'
    _inherit = 'res.config.installer'

    def execute(self, cr, uid, ids, context=None):
        cr.execute \
            ("""UPDATE ir_sequence
                 SET prefix = replace(prefix, '(year)', '(fy)'),
                     suffix = replace(suffix, '(year)', '(fy)') 
               WHERE (prefix LIKE '%(year)%' OR  suffix LIKE '%(year)%') 
                 AND id IN (SELECT sequence_main_id FROM account_sequence_fiscalyear);""" 
            )
