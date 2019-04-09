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
            res[partner_id] = []
        if len(ids) != 1:
            return res
        for partner in self.browse(cr, uid, ids, context):
            account_view_ids = [partner.property_account_receivable.id, partner.property_account_payable.id]
            fposition_id = partner.property_account_position
            for account_id in [partner.property_account_receivable.id, partner.property_account_payable.id]:
                account_view_ids.append(
                    self.pool['account.fiscal.position'].map_account(cr, uid, fposition_id, account_id,
                                                                     context=context))

            account_view_ids = list(set(account_view_ids))
            res[partner.id] = self.pool['account.move.line'].search(cr, uid, [('account_id', 'in', account_view_ids),
                                                                              ('partner_id', '=', partner.id),
                                                                              ('reconcile_id', '=', False)],
                                                                    context=context)
        return res

    _columns = {
        'payment_ids': fields.function(_get_invoice_payment, string="All Open Payment", type='one2many',
                                       method=True, relation='account.move.line')
    }
