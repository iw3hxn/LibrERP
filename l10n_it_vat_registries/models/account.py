# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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


class account_tax_code(orm.Model):
    _inherit = "account.tax.code"

    _columns = {
        'is_base': fields.boolean(
            'Is base',
            help="This tax code is used for base amounts (field used by "
                 "VAT registries)"),
        'exclude_from_registries': fields.boolean(
            'Exclude from VAT registries'),
    }


class account_tax(orm.Model):
    _inherit = "account.tax"

    def _set_is_base(self, cr, uid, vals, context):
        if vals.get('base_code_id', False) or vals.get('ref_base_code_id', False):
            account_tax_code_obj = self.pool['account.tax.code']
            account_tax_code_ids = []
            if vals.get('base_code_id'):
                account_tax_code_ids.append(vals.get('base_code_id'))
            if vals.get('ref_base_code_id'):
                account_tax_code_ids.append(vals.get('ref_base_code_id'))
            # CARLO done because when i create from new profile is possible that tax code is not commit on database
            for tax_code in account_tax_code_obj.browse(cr, uid, account_tax_code_ids, context):
                tax_code.write({'is_base': True})

        return True

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(account_tax, self).write(cr, uid, ids, vals, context)
        self._set_is_base(cr, uid, vals, context)
        return res

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(account_tax, self).create(cr, uid, vals, context)
        self._set_is_base(cr, uid, vals, context)
        return res

    _columns = {
        'description': fields.char('Tax Code', size=32, required=True),
    }
