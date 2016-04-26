# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Didotech srl (info at didotech.com)
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
# from openerp.tools.translate import _


class partner_import_template(orm.Model):
    _name = "partner.import.template"
    _description = "Partner Import Template"
    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'auto_update': fields.boolean(
            'Auto Create Maps',
            help="If flag auto create maps"),
        'account_fiscal_position_ids': fields.one2many(
            'migration.fiscal.position',
            'position_id',
            'Fiscal Position Mapping'),
        'payment_term_ids': fields.one2many(
            'migration.payment.term',
            'position_id',
            'Payment Term Mapping'),
        'note': fields.text('Note'),
    }

    _default = {
        'auto_update': 1
    }

    def map_account_fiscal_position(
        self, cr, uid, partner_template_id,
        account_fiscal_position, context=None
    ):
        if not account_fiscal_position and not partner_template_id:
            return False
        result = False
        if not partner_template_id and account_fiscal_position:
            fiscal_position_obj = self.pool['account.fiscal.position']
            fiscal_position_ids = fiscal_position_obj.search(
                cr, uid, [
                    ('name', '=', account_fiscal_position)
                ], context=context)
            if fiscal_position_ids:
                result = fiscal_position_obj.browse(
                    cr, uid, fiscal_position_ids, context=context
                )[0].id
        else:
            account_fiscal_position_obj = \
                self.pool['migration.fiscal.position']
            fiscal_position_ids = account_fiscal_position_obj.search(
                cr, uid, [
                    ('source_position', '=', account_fiscal_position),
                    ('position_id', '=', partner_template_id.id)
                ])
            if fiscal_position_ids:
                result = account_fiscal_position_obj.browse(
                    cr, uid, fiscal_position_ids, context=context
                )[0].dest_position_id.id
            elif partner_template_id.auto_update:
                account_fiscal_position_obj.create(
                    cr, uid, {
                        'source_position': account_fiscal_position,
                        'position_id': partner_template_id.id
                    }, context=context)
        return result

    def map_payment_term(self, cr, uid, partner_template_id, payment_term, context=None):
        if not payment_term and not partner_template_id:
            return {}
        result = {}
        if not partner_template_id and payment_term:
            account_payment_term_obj = self.pool['account.payment.term']
            account_payment_term_ids = account_payment_term_obj.search(
                cr, uid, [
                    ('name', '=', payment_term)
                ], context=context)
            if account_payment_term_ids:
                result['property_payment_term'] = \
                    account_payment_term_obj.browse(
                        cr, uid,
                        account_payment_term_ids, context=context
                    )[0].id
        else:
            migration_payment_term_obj = self.pool['migration.payment.term']
            migration_payment_term_ids = migration_payment_term_obj.search(
                cr, uid, [
                    ('source_term', '=', payment_term),
                    ('position_id', '=', partner_template_id.id)
                ], context=context)
            if migration_payment_term_ids:
                migration_payment_term = migration_payment_term_obj.browse(
                    cr, uid, migration_payment_term_ids, context=context)[0]
                result.update({
                    'property_payment_term': migration_payment_term.dest_position_id and migration_payment_term.dest_position_id.id or False,
                    'company_bank_id': migration_payment_term.company_bank_id and migration_payment_term.company_bank_id.id or False
                })

            elif partner_template_id.auto_update:
                migration_payment_term_obj.create(cr, uid, {
                    'source_term': payment_term,
                    'position_id': partner_template_id.id
                }, context=context)
        return result


class migration_fiscal_position(orm.Model):
    _name = 'migration.fiscal.position'
    _description = 'Fiscal Position Mapping'
    _rec_name = 'position_id'
    _columns = {
        'source_position': fields.char(
            'Source File Fiscal Position', size=64, required=True),
        'dest_position_id': fields.many2one(
            'account.fiscal.position', 'Fiscal Position'),
        'position_id': fields.many2one(
            'partner.import.template',
            'Partner Import Template', required=True, ondelete='cascade'
        ),
    }
    _order = 'source_position'


class migration_payment_term(orm.Model):
    _name = 'migration.payment.term'
    _description = 'Payment Term Mapping'
    _rec_name = 'position_id'
    _columns = {
        'source_term': fields.char(
            'Source File Payment Term',
            size=64, required=True
        ),
        'dest_position_id': fields.many2one(
            'account.payment.term',
            'Payment Term'
        ),
        'company_bank_id': fields.many2one(
            'res.partner.bank',
            string='Company bank for Bank Transfer',
            domain="[('state', '=', 'iban')]"
        ),
        'position_id': fields.many2one(
            'partner.import.template',
            'Partner Import Template',
            required=True, ondelete='cascade'
        ),
    }
    _order = 'source_term'
