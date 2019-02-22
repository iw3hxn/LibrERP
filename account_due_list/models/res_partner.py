# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2018 Didotech SRL
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

from openerp.osv import fields, orm


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _get_invoice_payment(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner_id in ids:
            res[partner_id] = self.pool['account.move.line'].search(cr, uid, [
                ('account_id.type', 'in', ['receivable', 'payable']), ('stored_invoice_id', '!=', False),
                ('partner_id', '=', partner_id), ('reconcile_id', '=', False)], order='date_maturity asc', context=context)
        return res

    _columns = {
        'payment_ids': fields.function(_get_invoice_payment, string="All Open Payment", type='one2many',
                                       method=True, relation='account.move.line')
    }
