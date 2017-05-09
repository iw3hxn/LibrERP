# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl
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

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import pooler

#
# class account_tax(orm.Model):
#     _inherit = 'account.tax'
#
#     def get_precision_tax():
#         def change_digit_tax(cr):
#             res = pooler.get_pool(cr.dbname).get('decimal.precision').precision_get(cr, 1, 'Account')
#             return (17, res+3)
#         return change_digit_tax
#
#     def copy(self, cr, uid, tax_id, defaults, context=None):
#         raise orm.except_orm(_('Warning'), _("Tax can't be duplicated"))
#         return False
#
#     def create(self, cr, uid, vals, context=None):
#         if not context:
#             context = {}
#         tax_code_obj = self.pool['account.tax.code']
#         tax_obj = self.pool['account.tax']
#         if tax_obj.search(cr, uid, [('name', '=', vals['name'])]):
#             raise orm.except_orm(_('Error!'),
#                                  _("Tax name '{name}' is not unique.").format(name=vals['name']))
#         if vals.get('description', False):
#             if tax_obj.search(cr, uid, [('description', '=', vals['description'])]):
#                 raise orm.except_orm(_('Error!'),
#                                      _("Tax description '{description}' is not unique.").format(description=vals['description']))
#
#         if vals.get('type_tax_use', False) == 'sale':
#             vals.update({'base_sign': 1, 'tax_sign': 1, 'ref_base_sign': -1, 'ref_tax_sign': -1})
#         elif vals.get('type_tax_use', False) == 'purchase':
#             vals.update({'base_sign': -1, 'tax_sign': -1, 'ref_base_sign': 1, 'ref_tax_sign': 1})
#
#         if vals.get('base_code_id', False) and vals.get('tax_code_id', False):
#             return super(account_tax, self).create(cr, uid, vals, context)
#
#         if not vals.get('base_code_id', False) and vals.get('account_base_tax_code_id', False):
#             parent_base_tax_code = tax_code_obj.browse(cr, uid, vals['account_base_tax_code_id'])
#             base_tax_code_vals = {
#                 'name': vals['name'] + ' (imp)',
#                 'code': parent_base_tax_code.code + vals['description'],
#                 'parent_id': vals['account_base_tax_code_id'],
#                 'is_base': True,
#                 'vat_statement_type': vals['type_tax_use'] == 'sale' and 'debit' or vals['type_tax_use'] == 'purchase' and 'credit',
#                 'vat_statement_sign': vals['type_tax_use'] == 'sale' and 1 or vals['type_tax_use'] == 'purchase' and -1,
#             }
#             i = 0
#             name = vals['name'] + ' (imp)'
#             while True:
#                 if tax_code_obj.search(cr, uid, [('name', '=', name)]):
#                     name += str(i)
#                     i += 1
#                 else:
#                     if i > 0:
#                         base_tax_code_vals['name'] += str(i)
#                     break
#             base_code_id = tax_code_obj.create(cr, uid, base_tax_code_vals, context=context)
#             vals.update({'base_code_id': base_code_id})
#
#         if not vals.get('tax_code_id', False) and vals.get('account_tax_code_id', False):
#             parent_tax_code = tax_code_obj.browse(cr, uid, vals['account_tax_code_id'])
#             if not parent_tax_code.code:
#                 raise orm.except_orm(_('Error!'),
#                                      _("Parent Tax '{name}' has non name.").format(name=parent_tax_code.name))
#             tax_code_vals = {
#                 'name': vals['name'],
#                 'code': parent_tax_code.code + (vals.get('description') and vals.get('description') or u''),
#                 'parent_id': vals['account_tax_code_id'],
#                 'is_base': False,
#                 'vat_statement_type': vals['type_tax_use'] == 'sale' and 'debit' or vals['type_tax_use'] == 'purchase' and 'credit',
#                 'vat_statement_sign': vals['type_tax_use'] == 'sale' and 1 or vals['type_tax_use'] == 'purchase' and -1,
#             }
#             i = 0
#             name = vals['name']
#             while True:
#                 if tax_code_obj.search(cr, uid, [('name', '=', name)]):
#                     name += str(i)
#                     i += 1
#                 else:
#                     if i > 0:
#                         tax_code_vals['name'] += str(i)
#                     break
#             tax_code_id = tax_code_obj.create(cr, uid, tax_code_vals, context=context)
#             vals.update({'tax_code_id': tax_code_id})
#
#         return super(account_tax, self).create(cr, uid, vals, context)
#
#     def write(self, cr, uid, ids, vals, context=None):
#         if not context:
#             context = {}
#         tax_code_obj = self.pool['account.tax.code']
#         tax_obj = self.pool['account.tax']
#         tax = tax_obj.browse(cr, uid, ids, context=context)[0]
#
#         if vals.get('name', False):
#             if tax_obj.search(cr, uid, [('name', '=', vals['name'])]):
#                 raise orm.except_orm(_('Error!'),
#                                      _("Tax name '{name}' is not unique.").format(name=vals['name']))
#
#         if vals.get('description', False):
#             if tax_obj.search(cr, uid, [('description', '=', vals['description'])]):
#                 raise orm.except_orm(_('Error!'),
#                                      _("Tax description '{description}' is not unique.").format(description=vals['description']))
#
#         if vals.get('type_tax_use', False):
#             if vals['type_tax_use'] != tax.type_tax_use:
#                 raise orm.except_orm(_('Error!'),
#                     _("Tax Type cannot be changed - create a different tax."))
#
# #         if (vals.get('type_tax_use', False) or tax.type_tax_use) == 'sale':
# #             vals.update({'base_sign': 1, 'tax_sign': 1, 'ref_base_sign': -1, 'ref_tax_sign': -1})
# #         elif (vals.get('type_tax_use', False) or tax.type_tax_use) == 'purchase':
# #             vals.update({'base_sign': -1, 'tax_sign': -1, 'ref_base_sign': 1, 'ref_tax_sign': 1})
#
#         if tax.base_code_id and tax.tax_code_id:
#             return super(account_tax, self).write(cr, uid, ids, vals, context)
#
#         if not tax.base_code_id:
#             if vals.get('account_base_tax_code_id', False) or tax.account_base_tax_code_id \
#                 and not vals.get('base_code_id', False):
#                     parent_base_tax_code = tax.account_base_tax_code_id or tax_code_obj.browse(cr, uid, vals['account_base_tax_code_id'])
#                     base_tax_code_vals = {
#                         'name': tax.name or vals.get('name') + ' (imp)',
#                         'code': parent_base_tax_code.code + tax.description or vals.get('description'),
#                         'parent_id': tax.account_base_tax_code_id.id or vals.get('account_base_tax_code_id'),
#                         'is_base': True,
#                         'vat_statement_type': (tax.type_tax_use or vals.get('type_tax_use')) == 'sale' and 'debit' or (tax.type_tax_use or vals.get('type_tax_use')) == 'purchase' and 'credit',
#                         'vat_statement_sign': (tax.type_tax_use or vals.get('type_tax_use')) == 'sale' and 1 or (tax.type_tax_use or vals.get('type_tax_use')) == 'purchase' and -1,
#                     }
#                     base_code_id = tax_code_obj.create(cr, uid, base_tax_code_vals, context=context)
#                     vals.update({'base_code_id': base_code_id})
#
#         if not tax.tax_code_id:
#             if vals.get('account_tax_code_id', False) or tax.account_tax_code_id \
#                 and not vals.get('tax_code_id', False):
#                     parent_tax_code = tax.account_tax_code_id or tax_code_obj.browse(cr, uid, vals['account_tax_code_id'])
#                     tax_code_vals = {
#                         'name': tax.name or vals.get('name'),
#                         'code': parent_tax_code.code + tax.description or vals.get('description'),
#                         'parent_id': tax.account_tax_code_id.id or vals.get('account_tax_code_id'),
#                         'is_base': False,
#                         'vat_statement_type': (tax.type_tax_use or vals.get('type_tax_use')) == 'sale' and 'debit' or (tax.type_tax_use or vals.get('type_tax_use')) == 'purchase' and 'credit',
#                         'vat_statement_sign': (tax.type_tax_use or vals.get('type_tax_use')) == 'sale' and 1 or (tax.type_tax_use or vals.get('type_tax_use')) == 'purchase' and -1,
#                     }
#                     tax_code_id = tax_code_obj.create(cr, uid, tax_code_vals, context=context)
#                     vals.update({'tax_code_id': tax_code_id})
#
#         return super(account_tax, self).write(cr, uid, ids, vals, context)
#
#
#     def onchange_tax_sign(self, cr, uid, ids, type_tax_use, context=None):
#         if type_tax_use:
#             if type_tax_use == "sale":
#                 return {'value': {'base_sign': 1, 'tax_sign': 1, 'ref_base_sign': -1, 'ref_tax_sign': -1}}
#             elif type_tax_use == "purchase":
#                 return {'value': {'base_sign': -1, 'tax_sign': -1, 'ref_base_sign': 1, 'ref_tax_sign': 1}}
#
#     _columns = {
#         'account_tax_code_id': fields.many2one('account.tax.code', 'Tax Code Parent', required=False,
#                                                help="Campo da valorizzare se si vuole sceglire il conto imposta da movimentare attraverso il codice imposta. \n" \
#                                                     " Il codice imposta richiamato dovrà avare a sua volta un codice padre con un padre non valorizzato"),
#         'account_base_tax_code_id': fields.many2one('account.tax.code', 'Base Tax Code Parent', required=False,),
#         'account_collected_id': fields.related('account_tax_code_id', 'vat_statement_account_id', type='many2one',
#                                                relation='account.account', string='Invoice Tax Account', store=True, readonly=True),
#         'account_paid_id': fields.related('account_tax_code_id', 'vat_statement_account_id', type='many2one',
#                                          relation='account.account', string='Refund Tax Account', store=True, readonly=True),
#         'ref_base_code_id': fields.related('base_code_id', type='many2one',
#                                          relation='account.tax.code', string='Refund Base Code', store=True, readonly=True),
#         'ref_tax_code_id': fields.related('tax_code_id', type='many2one',
#                                          relation='account.tax.code', string='Refund Tax Code', store=True, readonly=True),
#         'amount': fields.float('Amount', required=True, digits_compute=get_precision_tax(),
#                                help="For taxes of type percentage, enter % ratio between 0-1."),
#     }
