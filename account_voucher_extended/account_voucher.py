# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


from openerp.osv import fields, orm
import netsvc


class account_voucher(orm.Model):
    _inherit = "account.voucher"

    def button_check_proforma_voucher(self, cr, uid, ids, context=None):
        context = context or {}
        wf_service = netsvc.LocalService("workflow")
        if context.get('account_bank_statement_line_id', False):
            account_bank_statement_line = self.pool['account.bank.statement.line'].browse(cr, uid, context.get('account_bank_statement_line_id'), context)
            if account_bank_statement_line and account_bank_statement_line.statement_id.state != 'draft':
                for vid in ids:
                    wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
        return {'type': 'ir.actions.act_window_close'}

    def button_refuse_proforma_voucher(self, cr, uid, ids, context=None):
        context = context or {}
        if context.get('account_bank_statement_line_id', False):
            self.pool['account.bank.statement.line'].write(cr, uid, context.get('account_bank_statement_line_id'), {'voucher_id': False}, context)
            self.unlink(cr, uid, ids, context)
        return {'type': 'ir.actions.act_window_close'}

    def proforma_voucher2(self, cr, uid, ids, context=None):

        if context.get('active_model', False) and context.get('active_id', False):
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.voucher', ids[0], 'proforma_voucher', cr)
            self.pool['account.bank.statement.line'].write(cr, uid, context['active_id'], {'voucher_id': ids[0]})

        return True