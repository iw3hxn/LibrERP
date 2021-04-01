# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Stock Out Alert
#    Copyright (C) 2013 Enterprise Objects Consulting
#                       http://www.eoconsulting.com.ar
#    Authors: Mariano Ruiz <mrsarm@gmail.com>
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

from openerp.osv import osv, fields

import base64
import logging

_logger = logging.getLogger(__name__)


class StockComputeOut(osv.osv_memory):
    _name = 'stock.compute.out'
    _description = 'Stock Compute Out'

    _columns = {
        'name': fields.text("Text"),
        'name_json': fields.text("Json"),
        'state': fields.selection(
            (('draft', 'draft'), ('done', 'done'))),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }

    def compute_out(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """
        # form_data = self.browse(cr, uid, ids)[0]
        stock_move_model = self.pool['stock.move']
        prod_list = stock_move_model._check_op_stock_availability(cr, uid, context)
        res = stock_move_model._get_stock_out(cr, uid, prod_list, context)
        mail = stock_move_model._get_email_body(cr, uid, res, context)


        return self.write(cr, uid, ids, {'state': 'done', 'name': mail}, context=context)

