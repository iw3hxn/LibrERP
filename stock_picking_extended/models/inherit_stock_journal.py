# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import orm, fields


class stock_journal(orm.Model):
    _inherit = "stock.journal"
    
    _columns = {
        'name': fields.char('Stock Journal', size=32, required=True, translate=True),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
        'member_ids': fields.many2many('res.users', 'stock_journal_rel', 'journal_id', 'member_id', 'Team Members'),
        'default_invoice_state': fields.selection([
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")], "Invoice Control",
            select=True, required=False, readonly=False),
        'lot_input_id': fields.many2one('stock.location', 'Default Location Input', domain=[('usage', '!=', 'view')]),
        'lot_output_id': fields.many2one('stock.location', 'Default Location Output', domain=[('usage', '!=', 'view')]),
    }