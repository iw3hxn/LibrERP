# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product serial module for OpenERP
#    Copyright (C) 2008 Raphaël Valyi
#    2014 Didotech SRL
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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class pallet_move(orm.Model):
    
    _description = "Pallet Move"
    _name = 'pallet.move'    
    _order = 'date'

    _columns = {
        'name': fields.char("Number", size=256 , required=True),
        'date': fields.date('Date', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'move': fields.selection([('in', '+'), ('out', '-')], 'Move', readonly=True ),
        'account_invoice_id': fields.many2one('account.invoice', 'Invoice', domain=[('partner_id', '=', 'partner_id')] ),
        'stock_picking_id': fields.many2one('stock.picking', 'Picking', domain=[('partner_id', '=', 'partner_id')]),
        'pallet_qty': fields.integer('Number Pallet'),
        'pallet_id':fields.many2one('product.ul', 'Pallet', domain=[('type', '=', 'pallet')]),
    }
    
    _defaults = {
        'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
    }