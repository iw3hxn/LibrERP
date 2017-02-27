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


class commission(orm.Model):
    """Objeto comisión"""

    _name = "commission"
    _description = "Commission"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'type': fields.selection((('fix', 'Fix percentage'), ('sections', 'By sections')), 'Type', required=True),
        'fix_qty': fields.float('Fix Percentage'),
        'sections': fields.one2many('commission.section', 'commission_id', 'Sections'),
        'product_agent_ids': fields.one2many('product.agent.commission', 'commission_id', 'Agents'),
        'commission_ids': fields.one2many('hr.agent.commission', 'commission_id', 'Agents'),
    }
    _defaults = {
        'type': lambda *a: 'fix',
    }

    def calculate_sections(self, cr, uid, ids, base, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        commission = self.browse(cr, uid, ids, context)[0]
        for section in commission.sections:
            if abs(base) >= section.commission_from and (
                            abs(base) < section.commission_until or section.commission_until == 0):
                res = base * section.percent / 100.0
                return res
        return 0.0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

