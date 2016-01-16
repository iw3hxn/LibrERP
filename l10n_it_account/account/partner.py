# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2013 Associazione OpenERP Italia
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
import datetime
from codicefiscale import build, isvalid


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def check_fiscalcode(self, cr, uid, ids, context={}):
        for partner in self.browse(cr, uid, ids, context):
            if not partner.fiscalcode:
                return True
            if partner.fiscalcode.isdigit() or partner.fiscalcode[2:].isdigit():
                return True
            return isvalid(partner.fiscalcode.upper())
        return True

    def _set_fiscalcode(self, cr, uid, ids, field_name, field_value, arg, context):
        self.write(cr, uid, ids, {'fiscalcode': field_value}, context)
        return True

    def _get_fiscalcode(self, cr, uid, ids, field_name, arg, context):
        if not ids:
            return False

        result = {}

        partners = self.browse(cr, uid, ids, context=context)
        for partner in partners:
            result[partner.id] = partner.fiscalcode

        return result
        
    _columns = {
        'pec': fields.related('address', 'pec', type='char', size=64, string='PEC'),
        'cf': fields.function(_get_fiscalcode, fnct_inv=_set_fiscalcode, string='Codice Fiscale', type='char', method=True),
        'individual': fields.boolean('Persona Fisica'),
        'fiscalcode': fields.char('Fiscal Code', size=16, help="Italian Fiscal Code"),
        'fiscalcode_surname': fields.char('Surname', size=64),
        'fiscalcode_firstname': fields.char('First name', size=64),
        'birth_date': fields.date('Date of birth'),
        'birth_city': fields.many2one('res.city', 'City of birth'),
        'sex': fields.selection([
            ('M', 'Male'),
            ('F', 'Female'),
        ], "Sex"),
        'property_payment_term_payable': fields.property(
            'account.payment.term',
            type='many2one',
            relation='account.payment.term',
            string='Payment Term',
            view_load=True,
            help="This payment term will be used instead of the default one for the current partner for supplier moves."),
        'ref_companies': fields.one2many('res.company', 'partner_id', 'Companies that refers to partner'),
        'last_reconciliation_date': fields.datetime(
            'Latest Reconciliation Date', help='Date on which the partner accounting entries were reconciled last time')
    }
    _constraints = [(check_fiscalcode, "The fiscal code doesn't seem to be correct.", ["fiscalcode"])]

    _sql_constraints = [
        ('vat_uniq', 'unique (vat)', ('Error! Specified VAT Number already exists for any other registered partner.'))
    ]

    def compute_fiscal_code(self, cr, uid, ids, context):
        partners = self.browse(cr, uid, ids, context)
        for partner in partners:
            if not partner.fiscalcode_surname or not partner.fiscalcode_firstname or not partner.birth_date or not partner.birth_city or not partner.sex:
                raise orm.except_orm('Error', 'One or more fields are missing')
            birth_date = datetime.datetime.strptime(partner.birth_date, "%Y-%m-%d")
            CF = build(partner.fiscalcode_surname, partner.fiscalcode_firstname, birth_date, partner.sex, partner.birth_city.cadaster_code)
            partner.write({'fiscalcode': CF})
        return True
    
    def action_select_fiscal_position(self, cr, uid, ids, context=None):
        if not ids:
            return
        position_id = self.pool['select.fiscal.position'].create(cr, uid, {'partner_id': ids[0]}, context)
        return {
            'name': "Seleziona la Posizione Fiscale",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': "select.fiscal.position",
            'res_id': position_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': dict({}),
        }


class res_partner_address(orm.Model):
    _inherit = 'res.partner.address'
    _columns = {
        'pec': fields.char('PEC', size=64),
    }

