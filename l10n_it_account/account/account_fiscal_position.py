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

from openerp.osv import fields, orm
import decimal_precision as dp


class account_fiscal_position(orm.Model):
    _inherit = 'account.fiscal.position'
    
    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        dichiarazioni = self.browse(cr, uid, ids, context)
        for dichirazione in dichiarazioni:
            value[dichirazione.id] = 'black'
        return value
    
    _columns = {
        'is_tax_exemption': fields.boolean('Ha dichiarazione di intento IVA?'),
        'required_tax': fields.boolean('Requiered Tax on invoice'),
        'no_check_vat': fields.boolean('No required VAT'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'number': fields.char('Numero Dichiarante', size=32),
        'date': fields.date('Data Dichiarazione'),
        'end_validity': fields.date('Fine Periodo Dichiarazione'),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('concorrenza')),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,)
    }
    
    def _get_tax_exemption(self, cr, uid, context):
        if 'is_tax_exemption' in context:
            return True
        else:
            return False
    
    _defaults = {
        'is_tax_exemption': lambda self, cr, uid, context: self._get_tax_exemption(cr, uid, context),
    }
    
    def create(self, cr, uid, vals, context={}):
        if 'number' not in vals or not vals['number'] and vals.get('is_tax_exemption', False):
            vals['number'] = self.pool['ir.sequence'].next_by_code(cr, uid, self._name, context)
        return super(account_fiscal_position, self).create(cr, uid, vals, context=context)
