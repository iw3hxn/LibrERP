# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
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


class account_bank_statement_line(orm.Model):
    _inherit = 'account.bank.statement.line'

    _columns = {
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'journal_id': fields.related('statement_id', 'journal_id', type='many2one', relation='account.journal',
                                     string='Journal', store=True, readonly=True),

        'state': fields.related('statement_id', 'state', type='selection', selection=[('draft', 'New'), ('open', 'Open'), ('confirm', 'Closed')], string='Status', readonly=True),
    }

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        open_line_ids = self.search(cr, uid, [('id', 'in', ids), ('statement_id.state', 'in', ['draft', 'open'])])
        return super(account_bank_statement_line, self).unlink(cr, uid, open_line_ids, context)

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        obj_partner = self.pool.get('res.partner')
        if context is None:
            context = {}
        if not partner_id:
            return {}
        part = obj_partner.browse(cr, uid, partner_id, context=context)
        if not part.supplier and not part.customer:
            partner_type = 'general'
        elif part.supplier and part.customer:
            if self.pool['account.invoice'].search(cr, uid, [('partner_id', '=', part.id), ('state', '=', 'open'), ('type', 'in', ['out_invoice', 'out_refund'])], context=context):
                partner_type = 'customer'
            else:
                partner_type = 'supplier'
        else:
            if part.supplier:
                partner_type = 'supplier'
            if part.customer:
                partner_type = 'customer'

        res_type = self.onchange_type(cr, uid, ids, partner_id=partner_id, type=partner_type, context=context)
        if res_type['value'] and res_type['value'].get('account_id', False):
            return {'value': {'type': partner_type, 'account_id': res_type['value']['account_id']}}
        return {'value': {'type': partner_type}}

    def onchange_type(self, cr, uid, line_id, partner_id, type, context=None):
        res = {'value': {}}
        obj_partner = self.pool.get('res.partner')
        if context is None:
            context = {}
        if not partner_id:
            return res
        account_id = False
        line = self.browse(cr, uid, line_id, context=context)
        #if not line or (line and not line[0].account_id):
        part = obj_partner.browse(cr, uid, partner_id, context=context)
        if type == 'supplier':
            account_id = part.property_account_payable.id
        else:
            account_id = part.property_account_receivable.id

        fpos = part.property_account_position
        res['value']['account_id'] = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)

        return res
