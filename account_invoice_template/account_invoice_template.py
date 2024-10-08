# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class account_invoice_template(orm.Model):

    _inherit = 'account.document.template'
    _name = 'account.invoice.template'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'account_id': fields.many2one(
            'account.account', 'Account', required=True),
        'template_line_ids': fields.one2many(
            'account.invoice.template.line',
            'template_id', 'Template Lines'),
        'type': fields.selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ('out_refund', 'Customer Refund'),
            ('in_refund', 'Supplier Refund'),
        ], 'Type', required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
    }

    def type_change(self, cr, uid, ids, type, partner_id):
        if not type:
            return {}
        journal_obj = self.pool['account.journal']
        partner_obj = self.pool['res.partner']
        if type:
            if type in ('out_invoice', 'out_refund'):
                journal_ids = journal_obj.search(cr, uid, [('type', 'ilike', 'sale')])
                partner_ids = partner_obj.search(cr, uid, [('customer', '=', True)])
            else:
                journal_ids = journal_obj.search(cr, uid, [('type', 'ilike', 'purchase')])
                partner_ids = partner_obj.search(cr, uid, [('supplier', '=', True)])
        return {'domain': {
                           'journal_id': [('id', 'in', journal_ids)],
                           'partner_id': [('id', 'in', partner_ids)],
                           },
                'value': {
                          'journal_id': journal_ids[0],
                          'partner_id': partner_ids[0],
                          },
                }

    def partner_id_change(self, cr, uid, ids, type, partner_id):
        result = {}

        if not partner_id:
            return {}

        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
            else:
                acc_id = p.property_account_payable.id
        result = {'value': {
                    'account_id': acc_id,
                }
        }
        return result


class account_invoice_template_line(orm.Model):

    _name = 'account.invoice.template.line'
    _inherit = 'account.document.template.line'

    _columns = {
        'account_id': fields.many2one(
            'account.account', 'Account',
            required=True,
            domain=[('type', '<>', 'view'), ('type', '<>', 'closed')]),
        'analytic_account_id': fields.many2one(
            'account.analytic.account',
            'Analytic Account', ondelete="cascade"),
        'invoice_line_tax_id': fields.many2many(
            'account.tax',
            'account_invoice_template_line_tax', 'invoice_line_id', 'tax_id',
            'Taxes', domain=[('parent_id', '=', False)]),
        'template_id': fields.many2one(
            'account.invoice.template', 'Template',
            ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product'),
    }

    _sql_constraints = [
        ('sequence_template_uniq', 'unique (template_id,sequence)',
            'The sequence of the line must be unique per template !')
    ]

    def product_id_change(self, cr, uid, ids, product_id, type, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        result = {}
        if not product_id:
            return {}

        product = self.pool['product.product'].browse(cr, uid, product_id, context=context)

        # name
        result.update({'name': product.name})

        # account
        if type in ('out_invoice', 'out_refund'):
            account_id = product.product_tmpl_id.property_account_income.id
            if not account_id:
                account_id = product.categ_id.property_account_income_categ.id
        else:
            account_id = product.product_tmpl_id.property_account_expense.id
            if not account_id:
                account_id = product.categ_id.property_account_expense_categ.id

        if account_id:
            result['account_id'] = account_id

        # taxes
        account_obj = self.pool['account.account']
        taxes = account_id and account_obj.browse(
            cr, uid, account_id, context=context).tax_ids or False
        if type in ('out_invoice', 'out_refund') and product.taxes_id:
            taxes = product.taxes_id
        elif product.supplier_taxes_id:
            taxes = product.supplier_taxes_id
        tax_ids = taxes and [tax.id for tax in taxes] or False
        result.update({'invoice_line_tax_id': tax_ids})

        return {'value': result}
