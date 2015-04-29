# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014-2015 Didotech SRL (info at didotech.com)
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


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'block_ref_customer': fields.boolean('Block Reference'),
        'block_ref_supplier': fields.boolean('Block Reference'),
        'selection_account_receivable': fields.many2one(
            'account.account', 'Parent account', domain="[('type','=','view'),\
            ('user_type.code','=','account_type_view_assets')]"),
        'selection_account_payable': fields.many2one(
            'account.account', 'Parent account', domain="[('type','=','view'),\
            ('user_type.code','=','account_type_view_liability')]"),
    }

    _sql_constraints = [
        ('property_supplier_ref', 'unique(property_supplier_ref)',
            'Codice Fornitore Univoco'),
        ('property_customer_ref', 'unique(property_customer_ref)',
            'Codice Cliente Univoco'),
    ]

    def _get_chart_template_property(self, cr, uid, property_chart=None, context=None):
        chart_obj = self.pool['account.chart.template']
        # We need Administrator rights to read account.chart.template properties
        chart_obj_ids = chart_obj.search(cr, 1, [])
        if len(chart_obj_ids) > 0 and property_chart:
            # We need Administrator rights to read account.chart.template properties
            chart_templates = chart_obj.browse(cr, 1, chart_obj_ids, context)
            for chart_template in chart_templates:
                property_chart_id = getattr(chart_template, property_chart).id
                # if it's not a view type code, it's another branch without partner_subaccount
                account_template = self.pool['account.account.template'].browse(cr, 1, property_chart_id)
                if account_template.type == 'view':
                    account_account_ids = self.pool['account.account'].search(cr, uid, [('code', '=', account_template.code)])
                    if account_account_ids:
                        return account_account_ids[0]
                    else:
                        continue
                else:
                    continue
            else:
                raise orm.except_orm('Warning!', "Parent Account Type is not of type 'view'")
        else:
            return []

    def get_create_supplier_partner_account(self, cr, uid, vals, context):
        return self.get_create_partner_account(cr, uid, vals, 'supplier', context)
    
    def get_create_customer_partner_account(self, cr, uid, vals, context):
        return self.get_create_partner_account(cr, uid, vals, 'customer', context)
    
    def get_create_partner_account(self, cr, uid, vals, account_type, context):
        account_obj = self.pool['account.account']
        account_type_obj = self.pool['account.account.type']
        
        if account_type == 'customer':
            property_account = 'property_account_receivable'
            type_account = 'receivable'
            property_ref = 'property_customer_ref'
        elif account_type == 'supplier':
            property_account = 'property_account_payable'
            type_account = 'payable'
            property_ref = 'property_supplier_ref'
        else:
            # Unknown account type
            return False
            
        if not vals.get(property_account, False):
            vals[property_account] = self._get_chart_template_property(
                cr, uid, property_account, context)
            
        property_account_id = vals.get(property_account, False)
        if property_account_id:
            property_account = account_obj.browse(cr, uid, property_account_id, context)
            
            account_ids = account_obj.search(cr, uid, [('code', '=', '{0}{1}'.format(property_account.code, vals[property_ref]))])
            if account_ids:
                return account_ids[0]
            else:
                account_type_id = account_type_obj.search(
                    cr, uid, [('code', '=', type_account)], context=context)[0]
                
                return account_obj.create(cr, uid, {
                    'name': vals.get('name', ''),
                    'code': '{0}{1}'.format(property_account.code, vals[property_ref]),
                    'user_type': account_type_id,
                    'type': type_account,
                    'parent_id': property_account_id,
                    'active': True,
                    'reconcile': True,
                    'currency_mode': property_account.currency_mode,
                }, context)
        else:
            return False

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        company = self.pool['res.users'].browse(
            cr, uid, uid, context).company_id
        if not company.enable_partner_subaccount:
            return super(res_partner, self).create(
                cr, uid, vals, context=context)

        #1 se marcato come cliente - inserire se non esiste
        if vals.get('customer', False) and not vals.get('supplier', False):
            vals['block_ref_customer'] = True
            if not vals.get('property_customer_ref', False):
                vals['property_customer_ref'] = self.pool['ir.sequence'].get(
                    cr, uid, 'SEQ_CUSTOMER_REF') or ''
            if vals.get('selection_account_receivable', False):
                vals['property_account_receivable'] = \
                    vals['selection_account_receivable']
            vals['property_account_receivable'] = \
                self.get_create_customer_partner_account(cr, uid, vals, context)

        #2 se marcato come fornitore - inserire se non esiste
        if vals.get('supplier', False) and not vals.get('customer', False):
            vals['block_ref_supplier'] = True
            if not vals.get('property_supplier_ref', False):
                vals['property_supplier_ref'] = self.pool['ir.sequence'].get(
                    cr, uid, 'SEQ_SUPPLIER_REF') or ''
            if vals.get('selection_account_payable', False):
                vals['property_account_payable'] = \
                    vals['selection_account_payable']
            vals['property_account_payable'] = \
                self.get_create_supplier_partner_account(cr, uid, vals, context)

        #3 se marcato come cliente e fornitore - inserire se non esiste
        if vals.get('customer', False) and vals.get('supplier', False):
            vals['block_ref_customer'] = True
            if not vals.get('property_customer_ref', False):
                vals['property_customer_ref'] = self.pool['ir.sequence'].get(
                    cr, uid, 'SEQ_CUSTOMER_REF') or ''
            vals['block_ref_supplier'] = True
            if not vals.get('property_supplier_ref', False):
                vals['property_supplier_ref'] = self.pool['ir.sequence'].get(
                    cr, uid, 'SEQ_SUPPLIER_REF') or ''
            if vals.get('selection_account_receivable', False):
                vals['property_account_receivable'] = \
                    vals['selection_account_receivable']
            if vals.get('selection_account_payable', False):
                vals['property_account_payable'] = \
                    vals['selection_account_payable']
            vals['property_account_receivable'] = \
                self.get_create_customer_partner_account(cr, uid, vals, context)
            vals['property_account_payable'] = \
                self.get_create_supplier_partner_account(cr, uid, vals, context)

        return super(res_partner, self).create(cr, uid, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        ids_account_payable = []
        ids_account_receivable = []
        for partner in self.pool['res.partner'].browse(cr, uid, ids, context):
            
            if partner.property_account_payable and partner.property_account_payable.type != 'view':
                if partner.property_account_payable.balance == 0.0:
                    ids_account_payable.append(partner.property_account_payable.id)
                else:
                    ids.remove(partner.id)
            if partner.property_account_receivable and partner.property_account_receivable.type != 'view':
                if partner.property_account_receivable.balance == 0.0:
                    ids_account_receivable.append(partner.property_account_receivable.id)
                else:
                    ids.remove(partner.id)
                    
        res = super(res_partner, self).unlink(cr, uid, ids, context)
        ids_account = list(set(ids_account_payable + ids_account_receivable))
        
        if res and ids_account:
            self.pool['account.account'].unlink(cr, 1, ids_account, context) #for unlink force superuser
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if not context:  # write is called from create, then skip
            context = {}
            return super(res_partner, self).write(
                cr, uid, ids, vals, context=context)
        company = self.pool['res.users'].browse(
            cr, uid, uid, context).company_id
        if not company.enable_partner_subaccount:
            return super(res_partner, self).write(
                cr, uid, ids, vals, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        account_obj = self.pool['account.account']
        partner = self.browse(cr, uid, ids[0], context)

        if partner.block_ref_customer or vals.get('customer', False):
            # already a customer or flagged as a customer
            vals['block_ref_customer'] = True
            if not 'name' in vals:
            # if there isn't the name of partner - then it is not modified
            # so assign it
                vals['name'] = partner.name
            
            if partner.property_account_receivable.type != 'view':
            # there is already an account created for the partner
                if partner.property_account_receivable.name != vals['name']:
                    # the account name if different from the partner name,
                    #so we must update the account name
                    account_obj.write(
                        cr, uid, partner.property_account_receivable.id,
                        {'name': vals['name']})
            else:
                # the property_account_receivable is a view type,
                # so we have to create the partner account
                if not 'property_customer_ref' in vals:
                    # there isn't the partner code, so create it
                    vals['property_customer_ref'] = \
                        self.pool['ir.sequence'].get(
                            cr, uid, 'SEQ_CUSTOMER_REF') or ''
                if vals.get('selection_account_receivable', False):
                    vals['property_account_receivable'] = \
                        vals['selection_account_receivable']
                else:
                    vals['property_account_receivable'] = \
                        partner.property_account_receivable.id
                        # è il conto vista
                vals['property_account_receivable'] = \
                    self.get_create_customer_partner_account(
                        cr, uid, vals, context)

        if partner.block_ref_supplier or vals.get('supplier', False):
            # already a supplier or flagged as a supplier
            vals['block_ref_supplier'] = True
            if not 'name' in vals:
                vals['name'] = partner.name
            if partner.property_account_payable.type != 'view':
                if partner.property_account_payable.name != vals['name']:
                    account_obj.write(
                        cr, uid, partner.property_account_payable.id,
                        {'name': vals['name']})
            else:
                if not 'property_supplier_ref' in vals:
                    vals['property_supplier_ref'] = \
                        self.pool['ir.sequence'].get(
                            cr, uid, 'SEQ_SUPPLIER_REF') or ''
                if vals.get('selection_account_payable', False):
                    vals['property_account_payable'] = \
                        vals['selection_account_payable']
                else:
                    vals['property_account_payable'] = \
                        partner.property_account_payable.id
                vals['property_account_payable'] = \
                    self.get_create_supplier_partner_account(
                        cr, uid, vals, context)

        return super(res_partner, self).write(
            cr, uid, ids, vals, context=context)

    def copy(self, cr, uid, partner_id, defaults, context=None):
        raise orm.except_orm('Warning', _('Duplication of a partner \
            is not allowed'))
