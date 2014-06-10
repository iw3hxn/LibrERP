# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>)
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

from openerp.osv import orm


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        super(account_invoice, self).finalize_invoice_move_lines(cr, uid, invoice_browse, move_lines)
        account_obj = self.pool.get('account.account')
        property_obj = self.pool.get('ir.property')
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        for move_line in move_lines:
            account_id = move_line[2]['account_id']
            #if account's type is payable or receivable
            if account_obj.browse(cr, uid, account_id).user_type.code in ['payable', 'receivable']:
                #if account refer to another partner, correct it
                rec_pro_id = property_obj.search(cr, uid, [('name', '=', 'property_account_receivable'), ('value_reference', '=', 'account.account,' + str(account_id) + ''), ('company_id', '=', company_id)])
                pay_pro_id = property_obj.search(cr, uid, [('name', '=', 'property_account_payable'), ('value_reference', '=', 'account.account,' + str(account_id) + ''), ('company_id', '=', company_id)])
                rec_res_id = False
                pay_res_id = False
                if rec_pro_id:
                    rec_line_data = property_obj.read(cr, uid, rec_pro_id, ['name', 'value_reference', 'res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('res_id', False) and int(rec_line_data[0]['res_id'].split(',')[1]) or False
                if pay_pro_id:
                    pay_line_data = property_obj.read(cr, uid, pay_pro_id, ['name', 'value_reference', 'res_id'])
                    pay_res_id = pay_line_data and pay_line_data[0].get('res_id', False) and int(pay_line_data[0]['res_id'].split(',')[1]) or False
                if rec_res_id:
                    if move_line[2]['partner_id'] != rec_res_id:
                        move_line[2]['partner_id'] = rec_res_id
                if pay_res_id:
                    if move_line[2]['partner_id'] != pay_res_id:
                        move_line[2]['partner_id'] = pay_res_id

        return move_lines
