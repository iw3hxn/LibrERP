# -*- coding: utf-8 -*-
# Copyright 2014, Compassion CH - Cyril Sester <csester@compassion.ch>
# Copyright 2014, Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2015, Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2017, Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
# Copyright 2017, Associazione Odoo Italia <https://odoo-italia.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.tools.translate import _
from datetime import datetime

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class Mandate(orm.Model):
    """The banking mandate is attached to a bank account and represents an
    authorization that the bank account owner gives to a company for a
    specific operation (such as direct debit)
    """
    _name = 'account.banking.mandate'
    _description = "A generic banking mandate"
    _rec_name = 'unique_mandate_reference'
    _inherit = ['mail.thread']
    _order = 'signature_date desc'

    def _get_states(self, cr, uid, context=None):
        return [
            ('draft', _('Draft')),
            ('valid', _('Valid')),
            ('expired', _('Expired')),
            ('cancel', _('Cancelled')),
        ]

    _columns = {
        'partner_bank_id': fields.many2one(
            'res.partner.bank', 'Bank Account'),
        'partner_id': fields.related(
            'partner_bank_id', 'partner_id', type='many2one',
            relation='res.partner', string='Partner', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'unique_mandate_reference': fields.char(
            'Unique Mandate Reference', size=35, readonly=True, states={'draft': [('readonly', False)]}),
        'signature_date': fields.date(
            'Date of Signature of the Mandate', readonly=True, states={'draft': [('readonly', False)]}),
        'scan': fields.binary('Scan of the Mandate'),
        'last_debit_date': fields.date(
            'Date of the Last Debit', readonly=True),
        'state': fields.selection(
            lambda self, *a, **kw: self._get_states(*a, **kw),
            string='Status',
            help="Only valid mandates can be used in a payment line. A "
            "cancelled mandate is a mandate that has been cancelled by "
            "the customer."),
        'recurrent': fields.boolean('Recurrent')
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context:
        self.pool['res.company']._company_default_get(
            cr, uid, 'account.banking.mandate', context=context),
        'unique_mandate_reference': '/',
        'state': 'draft',
        'recurrent': True
    }

    _sql_constraints = [(
        'mandate_ref_company_uniq',
        'unique(unique_mandate_reference, company_id)',
        'A Mandate with the same reference already exists for this company !'
    )]

    def create(self, cr, uid, vals, context=None):
        if vals.get('unique_mandate_reference', '/') == '/':
            vals['unique_mandate_reference'] = \
                self.pool['ir.sequence'].next_by_code(
                    cr, uid, 'account.banking.mandate', context=context)
        return super(Mandate, self).create(cr, uid, vals, context=context)

    def _check_dates(self, cr, uid, ids):
        for Mandate in self.browse(cr, uid, ids):
            if (Mandate.signature_date and
                    Mandate.signature_date >
                    fields.date.context_today(self, cr, uid)):
                raise orm.except_orm(
                    _('Error:'),
                    _("The date of signature of mandate '%s' is in the "
                        "future !")
                    % Mandate.unique_mandate_reference)
            if (Mandate.signature_date and Mandate.last_debit_date and
                    Mandate.signature_date > Mandate.last_debit_date):
                raise orm.except_orm(
                    _('Error:'),
                    _("The mandate '%s' can't have a date of last debit "
                        "before the date of signature.")
                    % Mandate.unique_mandate_reference)
        return True

    def _check_valid_state(self, cr, uid, ids):
        for Mandate in self.browse(cr, uid, ids):
            if Mandate.state == 'valid' and not Mandate.signature_date:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot validate the mandate '%s' without a date of "
                        "signature.")
                    % Mandate.unique_mandate_reference)
            if Mandate.state == 'valid' and not Mandate.partner_bank_id:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot validate the mandate '%s' because it is not "
                        "attached to a bank account.")
                    % Mandate.unique_mandate_reference)
        return True

    _constraints = [
        (_check_dates, "Error msg in raise",
            ['signature_date', 'last_debit_date']),
        (_check_valid_state, "Error msg in raise",
            ['state', 'partner_bank_id']),
    ]

    def mandate_partner_bank_change(
            self, cr, uid, ids, partner_bank_id, last_debit_date, state):
        res = {'value': {}}
        if partner_bank_id:
            partner_bank_read = self.pool['res.partner.bank'].read(
                cr, uid, partner_bank_id, ['partner_id'])['partner_id']
            res['value']['partner_id'] = partner_bank_read[0]
        return res

    def validate(self, cr, uid, ids, context=None):
        for Mandate in self.browse(cr, uid, ids, context=context):
            if not Mandate.signature_date:
                raise orm.except_orm('Mandate Error', _('Missing Signature Date'))
            if Mandate.state != 'draft':
                raise orm.except_orm('StateError',
                                     _('Mandate should be in draft state'))
            vals = {}
            if not Mandate.unique_mandate_reference or Mandate.unique_mandate_reference == '/':
                vals['unique_mandate_reference'] = \
                    self.pool['ir.sequence'].next_by_code(
                        cr, uid, 'account.banking.mandate')
            vals['state'] = 'valid'
            Mandate.write(vals)
        return True

    def cancel(self, cr, uid, ids, context=None):
        to_cancel_ids = []
        for Mandate in self.browse(cr, uid, ids, context=context):
            if Mandate.state not in ('draft', 'valid'):
                raise orm.except_orm('StateError',
                                     _('Mandate should be in draft or valid '
                                       'state'))
            to_cancel_ids.append(Mandate.id)
        self.write(
            cr, uid, to_cancel_ids, {'state': 'cancel'}, context=context)
        return True

    def back2draft(self, cr, uid, ids, context=None):
        ''' Allows to set the mandate back to the draft state.
        This is for mandates cancelled by mistake
        '''
        to_draft_ids = []
        for Mandate in self.browse(cr, uid, ids, context=context):
            if Mandate.state != 'cancel':
                raise orm.except_orm('StateError',
                                     _('Mandate should be in cancel state'))
            to_draft_ids.append(Mandate.id)
        self.write(
            cr, uid, to_draft_ids, {'state': 'draft'}, context=context)
        return True

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []

        context = context or self.pool['res.users'].context_get(cr, uid)

        for mandate in self.browse(cr, uid, ids, context=context):
            if mandate.signature_date:
                signature_date = datetime.strptime(mandate.signature_date[0:10], DEFAULT_SERVER_DATE_FORMAT)
                signature_date = signature_date.strftime("%d/%m/%Y")
            else:
                signature_date = ''
            iban = mandate.partner_bank_id and mandate.partner_bank_id.acc_number or ''
            name = u'{code} | {name} | {iban}'.format(code=mandate.unique_mandate_reference, name=signature_date, iban=iban.replace(' ', ''))
            res.append((mandate.id, name))
        return res
