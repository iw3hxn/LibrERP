# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014-2019 Didotech srl (<http://www.didotech.com>).
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


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def _get_stock_picking(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        account_invoice_obj = self.pool['account.invoice']

        for picking in self.browse(cr, uid, ids, context):
            account_invoice_ids = account_invoice_obj.search(cr, uid, [('origin', 'like', picking.name)], context=context)
            result[picking.id] = account_invoice_ids and account_invoice_ids[0] or False
        return result

    _columns = {
        'account_invoice_id': fields.function(_get_stock_picking, string='Account Invoice', type='many2one', relation="account.invoice", readonly=True, method=True),
    }
