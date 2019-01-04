# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech SRL
#    (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import orm


class res_partner_bank(orm.Model):
    _inherit = "res.partner.bank"

    # _defaults = {
    #     'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'res.partner.bank', context=c),
    # }


    def _prepare_name(self, bank):
        "Return the name to use when creating a bank journal"
        return (bank.bank_name or bank.bank and bank.bank.name or '')

    def on_change_acc_number(self, cr, uid, ids, acc_number, context=None):
        res = {
            'value': {}
        }
        if acc_number:
            acc_number = acc_number.replace(' ', '')
            if acc_number[0:2] == 'IT':
                abi = acc_number[5:10]
                cab = acc_number[10:15]
                bank_ids = self.pool['res.bank'].search(cr, uid, [('abi', '=', abi), ('cab', '=', cab)], context=context)
                if bank_ids:
                    res['value']['bank'] = bank_ids[0]
        return res
