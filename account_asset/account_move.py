# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#    Copyright (C) 2014 Didotech srl (www.didotech.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _
from decimal import Decimal, ROUND_HALF_UP
import logging
_logger = logging.getLogger(__name__)


class account_move(orm.Model):
    _inherit = 'account.move'

    def unlink(self, cr, uid, ids, context=None, check=True):
        if not context:
            context= {}
        depr_obj = self.pool.get('account.asset.depreciation.line')
        for move_id in ids:
            depr_ids = depr_obj.search(cr, uid, [('move_id', '=', move_id), ('type', '=', 'depreciate')])
            if depr_ids and not context.get('unlink_from_asset'):
                raise orm.except_orm(_('Error!'), 
                    _("You are not allowed to remove an accounting entry linked to an asset."
                      "\nYou should remove such entries from the asset."))
            depr_obj.write(cr, uid, depr_ids, {'move_id': False}, context)  # trigger store function
        return super(account_move, self).unlink(cr, uid, ids, context=context, check=check)

# REMOVED because block "post" and "cancel" action, not "unlink" action
#    def write(self, cr, uid, ids, vals, context=None):
#        if isinstance(ids, (int, long)):
#            ids = [ids]
#        depr_obj = self.pool.get('account.asset.depreciation.line')
#        for move_id in ids:
#            depr_ids = depr_obj.search(
#                cr, uid, [('move_id', '=', move_id), ('type', '=', 'depreciate')])
#            if depr_ids:
#                raise orm.except_orm(_('Error!'),
#                    _("You cannot change an accounting entry linked to an asset depreciation line."))
#        return super(account_move, self).write(cr, uid, ids, vals, context)


class account_move_line(orm.Model):
    _inherit = 'account.move.line'

    _columns = {
        'asset_category_id': fields.many2one('account.asset.category', 'Asset Category'),
        'subsequent_asset': fields.boolean('Subsequent Purchase of Asset'),
    }

    def onchange_account_id(self, cr, uid, ids, account_id=False, partner_id=False):
        res = super(account_move_line, self).onchange_account_id(cr, uid, ids, account_id)
        account_obj = self.pool.get('account.account')
        if account_id:
            account = account_obj.browse(cr, uid, account_id)
            asset_category = account.asset_category_id
            if asset_category:
                res['value'].update({'asset_category_id': asset_category.id})
        return res

    def get_asset_value_with_ind_tax(self, cr, uid, vals, context):
        account_tax_obj = self.pool['account.tax']
        if not vals.get('tax_code_id', False):
            return vals['debit'] or - vals['credit']
        tax_code = self.pool['account.tax.code'].browse(cr, uid, [vals.get('tax_code_id')])[0]
        tax = tax_code.base_tax_ids
        if vals.get('quantity') == 0.0:
            quantity = 1.0
        else:
            quantity = vals.get('quantity')
            
        res = account_tax_obj.compute_all(cr, uid, taxes=tax,
            price_unit=abs(vals.get('tax_amount') / quantity),
            quantity=quantity)
        tax_list = res['taxes']
        ind_amount = 0.0
        if len(tax_list) == 2:
            for tax in tax_list:
                if tax.get('balance', False):
                    ind_tax = tax_list[abs(tax_list.index(tax) - 1)]
                    ind_amount = float(Decimal(str(ind_tax['amount'])).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP))
        asset_value = vals['debit'] + ind_amount or - vals['credit'] - ind_amount
        return asset_value

    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context = {}
        #if vals.get('asset_id') and not context.get('allow_asset'):
        #    raise orm.except_orm(_('Error!'),
        #        _("You are not allowed to link an accounting entry to an asset."
        #          "\nYou should generate such entries from the asset."))
        asset_obj = self.pool.get('account.asset.asset')
        move = self.pool.get('account.move').browse(cr, uid, vals['move_id'])
        journal_obj = self.pool['account.journal']
        
        if vals.get('asset_category_id') and not vals.get('asset_id'):
            if journal_obj.browse(cr, uid, [move.journal_id.id], context=context)[0].type in ('sale', 'sale_refund', 'purchase', 'purchase_refund'):
                # add not deductible VAT if present, make it depending from l10n_it_partially_deductible_vat
                asset_value = self.get_asset_value_with_ind_tax(cr, uid, vals, context)
            else:
                asset_value = vals['debit'] or - vals['credit']
            # create asset
            asset_vals = {
                'name': vals['name'],
                'category_id': vals['asset_category_id'],
                'purchase_value': asset_value,
                'partner_id': vals['partner_id'],
                'date_start': move.date,
            }
            if context.get('company_id'):
                asset_vals['company_id'] = context['company_id']
            changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['asset_category_id'], context=context)
            asset_vals.update(changed_vals['value'])
            ctx = dict(context, create_asset_from_move_line=True, move_id=vals['move_id'])
            asset_id = asset_obj.create(cr, uid, asset_vals, context=ctx)
            vals['asset_id'] = asset_id
        elif vals.get('asset_id') and not context.get('create_move_from_button'):
            if journal_obj.browse(cr, uid, [move.journal_id.id], context=context)[0].type in ('sale', 'sale_refund', 'purchase', 'purchase_refund'):
                # add not deductible VAT if present, make it depending from l10n_it_partially_deductible_vat
                asset_value = self.get_asset_value_with_ind_tax(cr, uid, vals, context)
            else:
                asset_value = vals['debit'] or - vals['credit']
            #vals['asset_id'] = vals['subsequent_asset_id']
            #  get variation to put in asset value
            vals.update({'subsequent_asset': True})
            ctx = dict(context, update_asset_value_from_move_line=True, move_id=vals['move_id'], asset_value=asset_value)
            
            if journal_obj.browse(cr, uid, [move.journal_id.id], context=context)[0].type in ('sale', 'sale_refund', 'purchase', 'purchase_refund'):
                if asset_value > 0.0:
                    purchase_value = asset_obj.browse(cr, uid, [vals['asset_id']])[0].purchase_value
                    asset_obj.write(cr, uid, [vals['asset_id']], {'purchase_value': purchase_value + asset_value}, context=ctx)
                elif asset_value < 0.0:
                    remove_value = asset_obj.browse(cr, uid, [vals['asset_id']])[0].remove_value
                    asset_obj.write(cr, uid, [vals['asset_id']], {'remove_value': remove_value + asset_value, 'date_remove': move.date}, context=ctx)
            else:
                if asset_value > 0.0:
                    increase_value = asset_obj.browse(cr, uid, [vals['asset_id']])[0].increase_value
                    asset_obj.write(cr, uid, [vals['asset_id']], {'increase_value': increase_value + asset_value}, context=ctx)
                elif asset_value < 0.0:
                    decrease_value = asset_obj.browse(cr, uid, [vals['asset_id']])[0].decrease_value
                    asset_obj.write(cr, uid, [vals['asset_id']], {'decrease_value': decrease_value + asset_value}, context=ctx)

        return super(account_move_line, self).create(cr, uid, vals, context, check)

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        #if vals.get('asset_id'):
        #    raise orm.except_orm(_('Error!'),
        #        _("You are not allowed to link an accounting entry to an asset."
        #          "\nYou should generate such entries from the asset."))
        asset_obj = self.pool.get('account.asset.asset')
        journal_obj = self.pool['account.journal']

        if vals.get('asset_category_id') and not vals.get('asset_id'):
            assert len(ids) == 1, 'This option should only be used for a single id at a time.'
            for aml in self.browse(cr, uid, ids, context):
                if vals['asset_category_id'] == aml.asset_category_id.id:
                    continue

                if journal_obj.browse(cr, uid, [aml.move_id.journal_id.id], context=context)[0].type in ('sale', 'sale_refund', 'purchase', 'purchase_refund'):
                    # add not deductible VAT if present, make it depending from l10n_it_partially_deductible_vat
                    vals = {}
                    vals['tax_code_id'] = aml.tax_code_id.id
                    vals['tax_amount'] = aml.tax_amount
                    vals['quantity'] = aml.quantity
                    vals['debit'] = aml.debit
                    vals['credit'] = aml.credit
                    asset_value = self.get_asset_value_with_ind_tax(cr, uid, vals, context)
                else:
                    #asset_value = vals['debit'] or - vals['credit']
                    #??? why debit-credit? not debit or -credit?
                    debit = 'debit' in vals and vals.get('debit', 0.0) or aml.debit
                    credit = 'credit' in vals and vals.get('credit', 0.0) or aml.credit
                    asset_value = debit - credit

                partner_id = 'partner' in vals and vals.get('partner', False) or aml.partner_id.id
                date_start = 'date' in vals and vals.get('date', False) or aml.date
                #asset_name = 'ref' in vals and vals.get('ref') or aml.ref or aml.name
                # create asset
                asset_vals = {
                    'name': vals.get('name') or aml.name,
                    'category_id': vals['asset_category_id'],
                    'purchase_value': asset_value,
                    'partner_id': partner_id,
                    'date_start': date_start,
                    'company_id': vals.get('company_id') or aml.company_id.id,
                }
                changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['asset_category_id'], context=context)
                asset_vals.update(changed_vals['value'])
                ctx = dict(context, create_asset_from_move_line=True, move_id=aml.move_id.id)
                asset_id = asset_obj.create(cr, uid, asset_vals, context=ctx)
                vals['asset_id'] = asset_id

        elif vals.get('asset_id') and not context.get('create_move_from_button'):
            #vals['asset_id'] = vals['subsequent_asset_id']
            #  get variation to put in asset value
            ctx = dict(context, update_asset_value_from_move_line=True, move_id=vals['move_id'])
            for aml in self.browse(cr, uid, ids, context):
                if vals['asset_id'] == aml.asset_id.id:
                    continue
                
                if journal_obj.browse(cr, uid, [aml.move_id.journal_id.id], context=context)[0].type in ('sale', 'sale_refund', 'purchase', 'purchase_refund'):
                    # add not deductible VAT if present, make it depending from l10n_it_partially_deductible_vat
                    vals = {}
                    vals['tax_code_id'] = aml.tax_code_id.id
                    vals['tax_amount'] = aml.tax_amount
                    vals['quantity'] = aml.quantity
                    vals['debit'] = aml.debit
                    vals['credit'] = aml.credit
                    asset_value = self.get_asset_value_with_ind_tax(cr, uid, vals, context)
                else:
                    asset_value = vals['debit'] or - vals['credit']
                ctx.update({'asset_value': asset_value})

                if journal_obj.browse(cr, uid, [aml.move_id.journal_id.id], context=context)[0].type in ('sale', 'sale_refund', 'purchase', 'purchase_refund'):
                    if asset_value > 0.0:
                        purchase_value = asset_obj.browse(cr, uid, [vals['asset_id']])[0].purchase_value + asset_value
                        asset_obj.write(cr, uid, [vals['asset_id']], {'purchase_value': purchase_value}, context=ctx)
                    elif asset_value < 0.0:
                        remove_value = asset_obj.browse(cr, uid, [vals['asset_id']])[0].remove_value + asset_value
                        asset_obj.write(cr, uid, [vals['asset_id']], {'remove_value': remove_value, 'date_remove': aml.move_id.date}, context=ctx)
                else:
                    if asset_value > 0.0:
                        increase_value = asset_obj.browse(cr, uid, [vals['asset_id']])[0].increase_value + asset_value
                        asset_obj.write(cr, uid, [vals['asset_id']], {'increase_value': increase_value}, context=ctx)
                    elif asset_value < 0.0:
                        decrease_value = asset_obj.browse(cr, uid, [vals['asset_id']])[0].decrease_value + asset_value
                        asset_obj.write(cr, uid, [vals['asset_id']], {'decrease_value': decrease_value}, context=ctx)

        return super(account_move_line, self).write(cr, uid, ids, vals, context, check, update_check)
