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
from product._common import rounding
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class mrp_production(orm.Model):
    _inherit = 'mrp.production'
    
    def _make_production_internal_shipment(self, cr, uid, production, context=None):
        picking_id = super(mrp_production, self)._make_production_internal_shipment(cr, uid, production, context)
        picking_vals = {}
        if production.analytic_account_id:

            project_ids = self.pool['project.project'].search(cr, uid, [('analytic_account_id', '=', production.analytic_account_id.id)],
                                             context=context)
            if project_ids:
                picking_vals.update({'project_id': project_ids[0]})
            self.pool['stock.picking'].write(cr, uid, picking_id, picking_vals, context)
        return picking_id
