# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2017    SHS-AV s.r.l. <https://www.zeroincombenze.it>
#    Copyright (C) 2017    Didotech srl <http://www.didotech.com>
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
import logging

from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
try:
    from codicefiscale import build, isvalid
except (ImportError, IOError) as err:
    _logger.error(err)


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

    def _split_last_first_name(self, cr, uid, partner=None,
                               name=None, splitmode=None):
        if partner:
            # if not partner.individual and partner.is_company:
            if not partner.individual:
                return '', ''
            f = partner.name.split(' ')
            if not splitmode:
                if hasattr(partner, 'splitmode'):
                    splitmode = partner.splitmode
                else:
                    splitmode = self._default_split_mode(cr, uid)
        else:
            if not name:
                return '', ''
            if not splitmode:
                splitmode = self._default_split_mode(cr, uid)
            f = name.split(' ')
        if len(f) == 1:
            if splitmode[0] == 'F':
                return '', f[0]
            elif splitmode[0] == 'L':
                return f[0], ''
        elif len(f) == 2:
            if splitmode[0] == 'F':
                return f[1], f[0]
            elif splitmode[0] == 'L':
                return f[0], f[1]
        elif len(f) == 3:
            if splitmode in ('LFM', 'LF', 'L2FM'):
                return f[2], '%s %s' % (f[0], f[1])
            elif splitmode in ('FML', 'FL', 'FML2'):
                return '%s %s' % (f[0], f[1]), f[2]
            elif splitmode == 'L2F':
                return '%s %s' % (f[0], f[1]), f[2]
            elif splitmode == 'FL2':
                return '%s %s' % (f[1], f[2]), f[0]
        else:
            if splitmode[0] == 'F':
                return '%s %s' % (f[2], f[3]), '%s %s' % (f[0], f[1])
            elif splitmode[0] == 'L':
                return '%s %s' % (f[0], f[1]), '%s %s' % (f[2], f[3])
        return '', ''

    def _split_name(self, cr, uid, ids, fname, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            fiscalcode_surname, fiscalcode_firstname = self._split_last_first_name(
                cr, uid, partner=partner)
            res[partner.id] = {
                'fiscalcode_firstname': fiscalcode_firstname,
                'fiscalcode_surname': fiscalcode_surname
            }
        return res

    def _set_last_first_name(self, cr, uid, partner_id, name, value, arg,
                             context=None):
        return True
        
    _columns = {
        'pec': fields.related('address', 'pec', type='char', size=64, string='PEC'),
        'cf': fields.function(_get_fiscalcode, fnct_inv=_set_fiscalcode, string='Codice Fiscale', type='char', method=True),
        'individual': fields.boolean('Persona Fisica',
                                     help="If checked the C.F. is referred to a Individual Person"),
        'fiscalcode': fields.char('Fiscal Code', size=16, help="Italian Fiscal Code"),
        # 'fiscalcode_surname': fields.char('Surname', size=64),
        # 'fiscalcode_firstname': fields.char('First name', size=64),
        'fiscalcode_firstname': fields.function(
            _split_name,
            string="First Name",
            type="char",
            store=True,
            select=True,
            readonly=True,
            fnct_inv=_set_last_first_name,
            multi=True
        ),
        'fiscalcode_surname': fields.function(
            _split_name,
            string="Last Name",
            type="char",
            store=True,
            select=True,
            readonly=True,
            fnct_inv=_set_last_first_name,
            multi=True
        ),
        'splitmode': fields.selection([
            ('LF', 'Last/First'),
            ('FL', 'First/Last'),
            ('LFM', 'Last/First Middle'),
            ('L2F', 'Last last/First'),
            ('L2FM', 'Last last/First Middle'),
            ('FML', 'First middle/Last'),
            ('FL2', 'First/Last last'),
            ('FML2', 'First Middle/Last last')
        ], "First Last format"),
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

    _defaults = {
        'individual': False,
        'splitmode': 'LF'
    }

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

    def onchange_fiscalcode(self, cr, uid, ids, fiscalcode, context=None):
        name = 'fiscalcode'
        if fiscalcode:
            if len(fiscalcode) == 11:
                res_partner_pool = self.pool.get('res.partner')
                chk = res_partner_pool.simple_vat_check(
                    cr, uid, 'it', fiscalcode)
                if not chk:
                    return {'value': {name: False},
                            'warning': {
                        'title': 'Invalid fiscalcode!',
                        'message': 'Invalid vat number'}
                    }
                individual = False
            elif len(fiscalcode) != 16:
                return {'value': {name: False},
                        'warning': {
                    'title': 'Invalid len!',
                    'message': 'Fiscal code len must be 11 or 16'}
                }
            else:
                fiscalcode = fiscalcode.upper()
                chk = codicefiscale.control_code(fiscalcode[0:15])
                if chk != fiscalcode[15]:
                    value = fiscalcode[0:15] + chk
                    return {'value': {name: value},
                            'warning': {
                                'title': 'Invalid fiscalcode!',
                                'message': 'Fiscal code could be %s' % (value)}
                            }
                individual = True
            return {'value': {name: fiscalcode,
                              'individual': individual}}
        return {'value': {'individual': False}}

    def onchange_name(self, cr, uid, ids, name, splitmode, context=None):
        return self.onchange_split_mode(cr, uid, ids, splitmode, name, context)

    def onchange_split_mode(self, cr, uid, ids, splitmode, name, context=None):
        lastname, firstname = self._split_last_first_name(
            cr, uid, name=name, splitmode=splitmode)
        return {
            'value': {
                'fiscalcode_firstname': firstname,
                'fiscalcode_surname': lastname
            }
        }

    def _default_split_mode(self, cr, uid, partner=None, context=None):
        return self._defaults['splitmode']


class res_partner_address(orm.Model):
    _inherit = 'res.partner.address'
    _columns = {
        'pec': fields.char('PEC', size=64),
    }

