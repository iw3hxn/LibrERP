# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
# $Id$
#
# This program is free software: you can redistribute it and/or modify
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


class commission_section(orm.Model):
    """periodo de las comisiones"""

    _name = "commission.section"
    _description = "Commission section"
    _order = 'commission_from asc'
    _columns = {
        'commission_from': fields.float('From'),
        'commission_until': fields.float('Until'),
        'percent': fields.float('Percent'),
        'commission_id': fields.many2one('commission', 'Commission', required=True)
    }

    def _check_commission_overlap(self, cr, uid, ids, context=None):
        for section in self.browse(cr, uid, ids, context=context):
            where = []
            if section.commission_from:
                where.append("((commission_until > '%s') or (commission_until is null))" % (section.commission_from,))
            if section.commission_until:
                where.append("((commission_from < '%s') or (commission_from is null))" % (section.commission_until,))

            cr.execute('SELECT id FROM commission_section WHERE ' + ' and '.join(where) + (where and ' and ' or '') +
                       'commission_id = %s AND id != %s', (
                           section.commission_id.id,
                           section.id))
            if cr.fetchall():
                return False
        return True

    _constraints = [
        (_check_commission_overlap, 'You cannot have section that overlap!',
            ['commission_from', 'commission_until'])
    ]


