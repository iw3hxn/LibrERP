# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


payable_account_vals = {'partner_type': 'Fornitori', 'user_type': 'payable', 'parent_id': '25', 'code': '250', 'property_account': 'property_account_payable'}
receivable_account_vals = {'partner_type': 'Clienti', 'user_type': 'receivable', 'parent_id': '15', 'code': '150', 'property_account': 'property_account_receivable'}


class res_partner(orm.Model):
    _inherit = 'res.partner'
    _columns = {
        'block_ref_customer': fields.boolean('Block Reference'),
        'block_ref_supplier': fields.boolean('Block Reference'),
    }

    _sql_constraints = [
        ('property_supplier_ref', 'unique(property_supplier_ref)', 'Codice Fornitore Univoco'),
        ('property_customer_ref', 'unique(property_customer_ref)', 'Codice Cliente Univoco'),
    ]

    def get_create_view_account(self, cr, uid, property_account_id, acc_vals, context=None):
        '''Get the parent code account: if this code is not of type view, create a view type code parent'''
        account_obj = self.pool['account.account']
        account_type_obj = self.pool['account.account.type']
        chart_obj = self.pool['account.chart.template']
        # We need Administrator rights to read account.chart.template properties
        chart_obj_ids = chart_obj.search(cr, 1, [])
        if len(chart_obj_ids) > 0:  # if there is an old chart, this is a migration
            # We need Administrator rights to read account.chart.template properties
            chart_templates = chart_obj.browse(cr, 1, chart_obj_ids, context)
            for chart_template in chart_templates:
                if not property_account_id:
                    property_account_id = getattr(
                        chart_template, 'property_account_{user_type}'.format(user_type=acc_vals['user_type'])).id
                # if it's not a view type code, it's another branch without partner_subaccount
                if chart_template.property_account_payable.type != 'view' or chart_template.property_account_receivable.type != 'view':
                    if not account_obj.search(cr, uid, [('code', '=', acc_vals['code'])]):  # the parent code doesn't exist, so create it
                        dict_account = {
                            'name': acc_vals['partner_type'],
                            'code': acc_vals['code'],
                            'user_type': account_type_obj.search(cr, uid, [('code', '=', acc_vals['user_type'])], context=context)[0],
                            'type': 'view',
                            'parent_id': account_obj.search(cr, uid, [('code', '=', acc_vals['parent_id'])])[0],
                            'active': True,
                            'reconcile': False,
                            # 'currency_mode': account_datas['currency_mode'],
                        }
                        account_id = account_obj.create(cr, uid, dict_account, context)
                        break
                    else:  # the parent code exists
                        account_id = account_obj.search(cr, uid, [('code', '=', acc_vals['code'])])[0]
                        break
                else:  # it's a migration from a previous branch with partner_subaccount already installed
                    account_id = account_obj.browse(cr, uid, property_account_id).id
                    break
        else:  # it's a new installation
            account_id = account_obj.browse(cr, uid, property_account_id).id

        return account_id

    def get_create_partner_account(self, cr, uid, parent_id, vals, context, type_account, account_type_id, partner_ref):
        account_obj = self.pool['account.account']

        parent_account = account_obj.browse(cr, uid, parent_id, context)

        code = '{0}{1}'.format(parent_account.code, partner_ref)

        account_ids = account_obj.search(cr, uid, [('code', '=', code)])
        if account_ids:
            return account_ids[0]
        else:
            return account_obj.create(cr, uid, {
                'name': vals.get('name', ''),
                'code': code,
                'user_type': account_type_id,
                'type': type_account,
                'parent_id': parent_id,
                'active': True,
                'reconcile': True,
                'currency_mode': parent_account.currency_mode,
            }, context)

    def create(self, cr, uid, vals, context=None):
        account_type_obj = self.pool['account.account.type']
        if not context:
            context = {}

        if not self.pool['res.users'].browse(cr, uid, uid, context).company_id.enable_partner_subaccount:
            return super(res_partner, self).create(cr, uid, vals, context=context)

        # 2 se marcato come cliente - inserire se non esiste
        if vals.get('customer', False):
            account_type_id = account_type_obj.search(cr, uid, [('code', '=', 'receivable')], context=context)[0]
            vals['block_ref_customer'] = True
            if not vals.get('property_customer_ref', False):
                vals['property_customer_ref'] = self.pool['ir.sequence'].get(cr, uid, 'SEQ_CUSTOMER_REF', context) or ''

            notview_account_id = self.get_create_view_account(
                cr, uid, vals.get('property_account_receivable', False), receivable_account_vals, context)

            vals['property_account_receivable'] = self.get_create_partner_account(
                cr, uid, notview_account_id, vals, context, 'receivable', account_type_id, vals['property_customer_ref'])

        # 3 se marcato come fornitore - inserire se non esiste
        if vals.get('supplier', False):
            account_type_id = account_type_obj.search(cr, uid, [('code', '=', 'payable')], context=context)[0]
            vals['block_ref_supplier'] = True
            if not vals.get('property_supplier_ref', False):
                vals['property_supplier_ref'] = self.pool['ir.sequence'].get(cr, uid, 'SEQ_SUPPLIER_REF') or ''
            notview_account_id = self.get_create_view_account(
                cr, uid, vals.get('property_account_payable', False), payable_account_vals, context)
            vals['property_account_payable'] = self.get_create_partner_account(
                cr, uid, notview_account_id, vals, context, 'payable', account_type_id, vals['property_supplier_ref'])

        return super(res_partner, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if not context:  # then write is called from create, then skip
            context = {}
            return super(res_partner, self).write(cr, uid, ids, vals, context=context)

        if not self.pool['res.users'].browse(cr, uid, uid).company_id.enable_partner_subaccount:
            return super(res_partner, self).write(cr, uid, ids, vals, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        account_type_obj = self.pool['account.account.type']
        account_obj = self.pool['account.account']
        partner = self.browse(cr, uid, ids[0], context)

        if partner.block_ref_customer or vals.get('customer', False):  # already a customer or flagged as a customer
            vals['block_ref_customer'] = True
            account_receivable_id = partner.property_account_receivable.id
            if 'name' not in vals:  # if there isn't the name of partner - if not modified then - assign it
                vals['name'] = partner.name
            if partner.property_account_receivable.type != 'view':  # there is already an account created for the partner
                if partner.property_account_receivable.name != vals['name']:
                    # the account name if different from the partner name, so we must update the account name
                    account_obj.write(cr, uid, account_receivable_id, {'name': vals['name']})
            else:  # the property_account_receivable is a view type, so we have to create the partner account
                if 'property_customer_ref' not in vals:  # there isn't the partner code, so create it
                    vals['property_customer_ref'] = self.pool['ir.sequence'].get(cr, uid, 'SEQ_CUSTOMER_REF') or ''
                # TODO we take the first account_type of type receivable found because there isn't another place to take it, it's not good
                account_type_id = account_type_obj.search(cr, uid, [('code', '=', 'receivable')], context=context)[0]
                notview_account_id = self.get_create_view_account(cr, uid, account_receivable_id, receivable_account_vals, context)
                vals['property_account_receivable'] = self.get_create_partner_account(
                    cr, uid, notview_account_id, vals, context, 'receivable', account_type_id, vals['property_customer_ref'])

        if partner.block_ref_supplier or vals.get('supplier', False):  # already a supplier or flagged as a supplier
            vals['block_ref_supplier'] = True
            account_payable_id = partner.property_account_payable.id
            if 'name' not in vals:
                vals['name'] = partner.name
            if partner.property_account_payable.type != 'view':
                if partner.property_account_payable.name != vals['name']:
                    account_obj.write(cr, uid, account_payable_id, {'name': vals['name']})
            else:
                if 'property_supplier_ref' not in vals:
                    vals['property_supplier_ref'] = self.pool['ir.sequence'].get(cr, uid, 'SEQ_SUPPLIER_REF') or ''
                account_type_id = account_type_obj.search(cr, uid, [('code', '=', 'payable')], context=context)[0]
                notview_account_id = self.get_create_view_account(cr, uid, account_payable_id, payable_account_vals, context)
                vals['property_account_payable'] = self.get_create_partner_account(
                    cr, uid, notview_account_id, vals, context, 'payable', account_type_id, vals['property_supplier_ref'])

        return super(res_partner, self).write(cr, uid, ids, vals, context=context)

    def copy(self, cr, uid, partner_id, defaults, context=None):
        raise orm.except_orm('Warning', _('Duplication of a partner is not allowed'))
