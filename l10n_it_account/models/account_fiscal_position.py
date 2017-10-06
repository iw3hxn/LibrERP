# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Didotech SRL
#    (<http://www.openerp-italia.org>).
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

import datetime

import decimal_precision as dp
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class account_fiscal_position(orm.Model):
    _inherit = 'account.fiscal.position'
    
    def get_color(self, cr, uid, ids, field_name, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        value = {}
        date_today = datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        print date_today
        for dichirazione in self.browse(cr, uid, ids, context):
            out_of_use = False
            if dichirazione.end_validity < date_today:
                out_of_use = True
            if dichirazione.amount and (dichirazione.amount < dichirazione.invoice_amount):
                out_of_use = True

            if out_of_use:
                value[dichirazione.id] = 'red'
            else:
                value[dichirazione.id] = 'black'
        return value

    def _get_invoice_amount(self, cr, uid, ids, field_name, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        account_invoice_obj = self.pool['account.invoice']
        value = {}
        for dichirazione in self.browse(cr, uid, ids, context):
            invoice_ids = account_invoice_obj.search(cr, uid, [
                ('partner_id', '=', dichirazione.partner_id.id),
                ('state', 'not in', ['draft', 'cancelled']),
                ('fiscal_position', '=', dichirazione.id)
            ], context=context)
            amount_untaxed = 0
            for invoice in account_invoice_obj.browse(cr, uid, invoice_ids, context):
                amount_untaxed += invoice.amount_untaxed
            value[dichirazione.id] = amount_untaxed
        return value
    
    _columns = {
        'partner_id_readonly': fields.boolean('Partner Readonly'),
        'is_tax_exemption': fields.boolean('Ha dichiarazione di intento IVA?'),
        'required_tax': fields.boolean('Requiered Tax on invoice'),
        'no_check_vat': fields.boolean('No required VAT'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'number': fields.char('Numero Dichiarante', size=32),
        'date': fields.date('Data Dichiarazione'),
        'end_validity': fields.date('Fine Periodo Dichiarazione'),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'invoice_amount': fields.function(_get_invoice_amount, string='Invoiced Amount', type='float', readonly=True, method=True, digits_compute=dp.get_precision('Account')),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,)
    }
    
    def _get_tax_exemption(self, cr, uid, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if 'is_tax_exemption' in context:
            return True
        else:
            return False
    
    _defaults = {
        'is_tax_exemption': lambda self, cr, uid, context: self._get_tax_exemption(cr, uid, context),
    }
    
    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if 'number' not in vals or not vals['number'] and vals.get('is_tax_exemption', False):
            vals['number'] = self.pool['ir.sequence'].next_by_code(cr, uid, self._name, context)

        vals['partner_id_readonly'] = True
        res = super(account_fiscal_position, self).create(cr, uid, vals, context=context)
        if 'partner_id' in vals:
            self.pool['res.partner'].write(cr, uid, vals.get('partner_id'), {'property_account_position': res}, context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        fiscal_position = self.pool['res.partner'].default_get(cr, uid, ['property_account_position'], context=context)['property_account_position']
        for dichirazione in self.browse(cr, uid, ids, context):
            if dichirazione.partner_id:
                dichirazione.partner_id.write({'property_account_position': fiscal_position})
        return super(account_fiscal_position, self).unlink(cr, uid, ids, context)
