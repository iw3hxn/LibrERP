# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Didotech srl (<http://www.didotech.com>).
#
#    All Rights Reserved
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

from osv import fields, osv


class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    _columns = {
        'merge_notes': fields.text("Merge Notes")
    }


class stock_move(osv.osv):
    _inherit = "stock.move"
    
    def _get_selection_list(self, cr, uid, context=None):
        #@return a list of tuples. tuples containing model name and name of the record
        model_obj = self.pool.get('ir.model')
        ids = model_obj.search(cr, uid, [('name', 'not ilike', '.')])
        res = model_obj.read(cr, uid, ids, ['model', 'name'])
        return [(r['model'], r['name']) for r in res] + [('', '')]

    _columns = {
        'origin_document': fields.reference("Origin Document", selection=_get_selection_list, size=None)
    }
