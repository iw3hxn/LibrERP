# -*- coding: utf-8 -*-
##############################################################################

#    Copyright (C) 2015 Didotech srl
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


class stock_move(orm.Model):
    _inherit = "stock.move"

    def _default_journal_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        picking_type = context.get('picking_type', False)
        stock_journal_id = context.get('stock_journal_id', False)
        res = []
        if picking_type == 'out' and stock_journal_id:
            journal = self.pool['stock.journal'].browse(cr, uid, stock_journal_id)
            res = journal.warehouse_id and journal.warehouse_id.lot_stock_id and journal.warehouse_id.lot_stock_id.id or []
        if not res:
            res = super(stock_move, self)._default_location_source( cr, uid, context)
        return res

    _defaults = {
        'location_id': _default_journal_location_source,
    }
