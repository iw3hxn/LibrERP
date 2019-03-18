
##############################################################################
#
#    Author: Didotech SRL
#    Copyright 2014 Didotech SRL
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

from openerp.osv import orm, fields


class account_invoice(orm.Model):

    _inherit = 'account.invoice'

    def action_move_create(self, cr, uid, ids, context=None):
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)

        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        enable_partner_subaccount = company.enable_partner_subaccount
        if enable_partner_subaccount:
            for invoice in self.browse(cr, uid, ids, context):

                # check that each invoice have correct account_id field
                if invoice.account_id.type == 'view' and enable_partner_subaccount:
                    # i get a view account, but i can't validate an invoice, i need to ckeck if subaccount is activated
                    if invoice.type in ['out_invoice', 'out_refund']:
                        # is a customer partner
                        if invoice.partner_id.property_account_receivable.type != 'view':
                            property_account_receivable_id = invoice.partner_id.property_account_receivable.id
                        else:
                            vals = {
                                'name': invoice.partner_id.name,
                                'selection_account_receivable': invoice.partner_id.selection_account_receivable and invoice.partner_id.selection_account_receivable.id or False,
                                'property_account_receivable': invoice.account_id.id,
                                'property_customer_ref': invoice.partner_id.property_customer_ref
                            }

                            property_account_receivable_id = self.pool['res.partner'].get_create_partner_account(cr, uid, vals, 'customer', context)
                            if property_account_receivable_id:
                                invoice.partner_id.write({'property_account_receivable': property_account_receivable_id})
                        if property_account_receivable_id:
                            invoice.write({'account_id': property_account_receivable_id})
                    else:
                        # is a supplier partner
                        if invoice.partner_id.property_account_payable.type != 'view':
                            property_account_payable_id = invoice.partner_id.property_account_payable.id
                        else:
                            vals = {
                                'name': invoice.partner_id.name,
                                'selection_account_payable': invoice.partner_id.selection_account_payable and invoice.partner_id.selection_account_payable.id or False,
                                'property_account_payable': invoice.account_id.id,
                                'property_supplier_ref': invoice.partner_id.property_supplier_ref,
                            }
                            property_account_payable_id = self.pool['res.partner'].get_create_partner_account(cr, uid, vals, 'supplier', context)
                            if property_account_payable_id:
                                invoice.partner_id.write({'property_account_payable': property_account_payable_id})
                        if property_account_payable_id:
                            invoice.write({'account_id': property_account_payable_id})

        return super(account_invoice, self).action_move_create(cr, uid, ids, context=context)
