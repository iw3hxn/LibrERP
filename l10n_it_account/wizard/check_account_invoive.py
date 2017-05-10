# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Didotech SRL
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp import netsvc
from openerp.osv import fields, orm


class check_account_invoice(orm.TransientModel):
    _name = "check.account.invoice"
    _description = "Value to Complete"
    _inherit = "ir.wizard.screen"

    def _get_accounts(self, cr, uid, context=None):
        fiscal_position_obj = self.pool['account.fiscal.position']
        partner_id = False #context.get('active_id', False)
        if partner_id:
            fiscal_position_ids = fiscal_position_obj.search(cr, uid, ['|', ('partner_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        else:
            fiscal_position_ids = fiscal_position_obj.search(cr, uid, [('partner_id', '=', False)], context=context)

        result = []

        for fiscal_position in fiscal_position_obj.browse(cr, uid, fiscal_position_ids, context):
            result.append((fiscal_position.id, fiscal_position.name))
        return result

    _columns = {
        'check_invoice_fiscal_position': fields.boolean('Check Fiscal Position on Invoice'),
        'property_account_position_id': fields.selection(_get_accounts, 'Fiscal Position'),
        'check_invoice_payment_term': fields.boolean('Check Payment Term on Invoice'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
        'required_vat': fields.boolean('Required Vat'),
        'vat': fields.char('Vat', size=15, required=False),
        'check_supplier_invoice_number': fields.boolean('Supplier invoice nr'),
        'supplier_invoice_number': fields.char('Supplier invoice nr', size=16),
    }

    def action_invoice_validate(self, cr, uid, ids, context):
        wizard = self.browse(cr, uid, ids[0], context=context)
        invoice_vals = {}
        if wizard.property_account_position_id:
            invoice_vals.update(fiscal_position=int(wizard.property_account_position_id))
        if wizard.payment_term:
            invoice_vals.update(payment_term=wizard.payment_term.id)
        if wizard.supplier_invoice_number:
            invoice_vals.update(payment_term=wizard.supplier_invoice_number)
        if invoice_vals:
            self.pool['account.invoice'].write(cr, uid, context['active_id'], invoice_vals, context)
        if wizard.vat:
            partner_id = self.pool['account.invoice'].browse(cr, uid, context['active_id'], context).partner_id.id
            self.pool['res.partner'].write(cr, uid, partner_id, {'vat': wizard.vat}, context)

        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.invoice', context['active_id'], 'invoice_open', cr)

        return {'type': 'ir.actions.act_window_close'}
