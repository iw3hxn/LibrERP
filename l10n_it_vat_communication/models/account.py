# -*- coding: utf-8 -*-
#    Copyright (C) 2017-2018 SHS-AV s.r.l. <https://www.zeroincombenze.it>
#    Copyright (C) 2017-2019 Didotech srl <http://www.didotech.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# [2017: SHS-AV s.r.l.] First version
# [2018: SHS-AV s.r.l.] Spesometro light
#
import logging
from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.release as release
_logger = logging.getLogger(__name__)
try:
    if release.major_version in ('6.1', '7.0'):
        import decimal_precision as dp
    else:
        import openerp.addons.decimal_precision as dp
    from openerp.addons.l10n_it_ade import ade
    import codicefiscale
except ImportError as err:
    _logger.debug(err)

# TODO: Use module for classification
EU_COUNTRIES = ['AT', 'BE', 'BG', 'CY', 'HR', 'DK', 'EE',
                'FI', 'FR', 'DE', 'GR', 'IE', 'IT', 'LV',
                'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'GB',
                'CZ', 'RO', 'SK', 'SI', 'ES', 'SE', 'HU']
z = '0'
for i, x in enumerate(ade.ADE_LEGALS['codice_carica']):
    if ade.ADE_LEGALS['codice_carica'][i][0] == z:
        j = ade.ADE_LEGALS['codice_carica'][i].index(z)
        del ade.ADE_LEGALS['codice_carica'][j]
        break


class AccountVatCommunication(orm.Model):

    _name = "account.vat.communication"

    _columns = {
        'company_id': fields.many2one('res.company', 'Azienda', required=True),
        'progressivo_telematico':
            fields.integer('Progressivo telematico', readonly=True),
        'soggetto_codice_fiscale':
            fields.char('Codice fiscale dichiarante',
                        size=16, required=True,
                        help="CF del soggetto che presenta la comunicazione "
                             "se PF o DI o con la specifica carica"),
        'codice_carica': fields.selection(
            ade.ADE_LEGALS['codice_carica'],
            'Codice carica',),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('confirmed', 'Confirmed'), ],
            'State', readonly=True),
        'period_ids': fields.one2many(
            'account.period', 'vat_commitment_id', 'Periods'),
        'account_vat_communication_dte_line_ids': fields.one2many(
            'account.vat.communication.dte.line', 'commitment_id',
            'Sale invoices',
            help='Sale invoices to export in VAT communication',
            states={
                'draft': [('readonly', False)],
                'open': [('readonly', False)],
                'confirmed': [('readonly', True)]
            }),
        'account_vat_communication_dtr_line_ids': fields.one2many(
            'account.vat.communication.dtr.line', 'commitment_id',
            'Purchase invoices',
            help='Purchase invoices to export in VAT communication',
            states={
                'draft': [('readonly', False)],
                'open': [('readonly', False)],
                'confirmed': [('readonly', True)]
            }),
        'attachment_ids': fields.one2many(
            'ir.attachment', 'res_id', 'Attachments',),
        'dte_amount_total': fields.float(
            'Total sales',
            help='Total amount of sale invoices in Communication',
            digits_compute=dp.get_precision('Account')),
        'dte_amount_taxable': fields.float(
            'Total taxable sales',
            help='Total taxables of sale invoices in Communication',
            digits_compute=dp.get_precision('Account')),
        'dte_amount_tax': fields.float(
            'Total tax sales',
            help='Total taxes of sale invoices in Communication',
            digits_compute=dp.get_precision('Account')),
        'dte_amount_discarded': fields.float(
            'Total discarded sales',
            help='Total amount discarded from sale invoices',
            digits_compute=dp.get_precision('Account')),
        'dtr_amount_total': fields.float(
            'Total purchases',
            help='Total amount of purchase invoices in Communication',
            digits_compute=dp.get_precision('Account')),
        'dtr_amount_taxable': fields.float(
            'Total taxable purchases',
            help='Total taxables of purchase invoices in Communication',
            digits_compute=dp.get_precision('Account')),
        'dtr_amount_tax': fields.float(
            'Total tax purchases',
            help='Total taxes of purchase invoices in Communication',
            digits_compute=dp.get_precision('Account')),
        'dtr_amount_discarded': fields.float(
            'Total discarded purchases',
            help='Total amount discarded from purchase invoices',
            digits_compute=dp.get_precision('Account')),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c:
            self.pool['res.company']._company_default_get(
                cr, uid, 'account.vat.communication', context=c),
        'state': 'draft',
    }

    def create(self, cr, uid, vals, context=None):
        res = super(AccountVatCommunication, self).create(
            cr, uid, vals, context)
        if 'company_id' in vals:
            sequence_ids = self.pool['ir.sequence'].search(
                cr, uid, [
                    ('name', '=', 'vat_communication'),
                    ('company_id', '=', vals['company_id'])
                ])
            if not sequence_ids:
                self.create_sequence(cr, uid, vals, context)
        return res

    def create_sequence(self, cr, uid, vals, context=None):
        """ Create new no_gap entry sequence for progressivo_telematico
        """
        seq = {
            'name': 'vat_communication',
            'implementation': 'no_gap',
            'prefix': '',
            'number_increment': 1
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
            return self.pool['ir.sequence'].create(cr, uid, seq)
        return False

    def test_open(self, cr, uid, ids, *args):
        return True

    def communication_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})

    def communication_open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'open'})

    def build_tax_tree(self, cr, uid, company_id, context=None):
        """
        account.tax.code records cannot be recognized as VAT or base amount and
        Italian law requires to couple base and VAT amounts,
        thats is stored on account.tax model.
        This function rebuilds (base,VAT) couples throught account.tax.
        Warning: end-user could have set many-2-many base,VAT relationship;
        in this case some couple (base,VAT) may be wrong.
        However, all tutorial of Odoo Italian Comunity and standard Italian
        Localization have just one-2-one relationshiop on (base,VAT).
        return: tax_tree[type][basevat][left], where
        - type may be 'sale', 'purchase' or 'all'
        - basevat may be 'tax_code_id', 'base_code_id', 'ref_tax_code_id' or
              'ref_base_code_id'
        - left is id of account.tax.code record
        """
        context = context or {}
        tax_model = self.pool['account.tax']
        tax_ids = tax_model.search(
            cr, uid, [('company_id', '=', company_id)])
        tax_tree = {}
        for tax_id in tax_ids:
            tax = tax_model.browse(cr, uid, tax_id)
            type = tax.type_tax_use
            if type not in tax_tree:
                tax_tree[type] = {}
            for basevat in ('tax_code_id', 'base_code_id',
                            'ref_tax_code_id', 'ref_base_code_id'):
                if basevat[-11:] == 'tax_code_id':
                    vatbase = basevat[0:-11] + 'base_code_id'
                elif basevat[-12:] == 'base_code_id':
                    vatbase = basevat[0:-12] + 'tax_code_id'
                else:
                    vatbase = False             # never should run here!
                if basevat not in tax_tree[type]:
                    tax_tree[type][basevat] = {}
                if getattr(tax, basevat):
                    left = getattr(tax, basevat).id
                    if getattr(tax, vatbase):
                        right = getattr(tax, vatbase).id
                        tax_tree[type][basevat][left] = right
                    elif left not in tax_tree[type][basevat]:
                        tax_tree[type][basevat][left] = False
        return tax_tree

    def set_progressivo_telematico(self, cr, uid, commitment, context=None):
        context = context or {}
        company_id = commitment.company_id
        sequence_model = self.pool['ir.sequence']
        sequence_ids = sequence_model.search(
            cr, uid, [
                ('name', '=', 'vat_communication'),
                ('company_id', '=', company_id.id)
            ])
        if len(sequence_ids) != 1:
            raise orm.except_orm(
                _('Error!'), _('VAT communication sequence not set!'))
        number = sequence_model.next_by_id(
            cr, uid, sequence_ids[0], context=context)
        self.write(cr, uid, commitment.id, {'progressivo_telematico': number})
        return number

    def get_country_code(self, cr, uid, partner):
        if release.major_version == '6.1':
            address_id = self.pool['res.partner'].address_get(
                cr, uid, [partner.id])['default']
            address = self.pool['res.partner.address'].browse(
                cr, uid, address_id, context=None)
        else:
            address = partner
        code = partner.vat and partner.vat[0:2].upper()
        return address.country_id.code or code

    def load_invoices(self, cr, uid, commitment, commitment_line_model,
                      dte_dtr_id, where, comm_lines, context=None):
        """Read all in/out invoices and return amount and fiscal parts"""
        invoice_model = self.pool['account.invoice']
        account_tax_model = self.pool['account.tax']
        sum_amounts = {}
        for f in ('total', 'taxable', 'tax', 'discarded'):
            sum_amounts[f] = 0.0
        invoice_ids = invoice_model.search(cr, uid, where, context=context)
        for invoice in invoice_model.browse(cr, uid, invoice_ids, context):
            partner = invoice.partner_id
            if not partner.vat and not partner.cf:
                _logger.error(u'{0} without vat'.format(partner.name))
                # continue
            inv_line = {}
            ait_obj = self.pool['account.invoice.tax']

            tax_payability = 'I'
            if release.major_version == '6.1':
                for tax_line in invoice.tax_line:
                    tax_id = self.pool['account.tax'].get_tax_by_invoice_tax(
                        cr, uid, tax_line.name, context=context)
                    tax = self.pool['account.tax'].browse(cr, uid, tax_id, context=context)
                    if tax.payability and tax.payability != 'I':
                        tax_payability = tax.payability

            for tax_dict in ait_obj.compute(cr, uid, invoice.id, context).values():
                invoice_tax = account_tax_model.browse(cr, uid, tax_dict['account_tax_id'], context)
                tax_nature = False
                tax_rate = 0.0
                tax_nodet_rate = 0.0
                if invoice_tax.tax_code_id:
                    if release.major_version == '6.1' and invoice_tax.tax_code_id.notprintable:
                        continue
                    if release.major_version == '6.1' and invoice_tax.tax_code_id.exclude_from_registries:
                        continue
                else:
                    if invoice_tax.base_code_id.notprintable:
                        continue
                    if invoice_tax.base_code_id.exclude_from_registries:
                        continue
                if release.major_version == '6.1' and tax_dict.get('amount', 0.00) < 0.00:
                    continue

                tax = invoice_tax
                if tax and not tax.parent_id:
                    if tax.amount > tax_rate:
                        tax_rate = tax.amount
                    if tax.non_taxable_nature:
                        tax_nature = tax.non_taxable_nature
                    if tax.payability:
                        tax_payability = tax.payability
                    if tax.type_tax_use:
                        tax_type = tax.type_tax_use
                    if not tax.account_collected_id or not tax.account_paid_id:
                        tax_nodet_rate = 1
                else:
                    if release.major_version == '6.1':
                        if tax.non_taxable_nature:
                            tax_nature = tax.non_taxable_nature
                        tax_rate = 0
                        for child in tax.parent_id.child_ids:
                            if child.type == 'percent':
                                if child.tax_code_id.notprintable:
                                    continue
                                if child.tax_code_id.exclude_from_registries:
                                    continue
                                if child.amount > 0:
                                    tax_rate += child.amount
                        if tax_rate:
                            tax_nodet_rate = 1 - (tax.amount / tax_rate)
                        else:
                            tax_nodet_rate = 0
                    else:
                        if tax.type == 'percent' and \
                                        tax.amount > tax_nodet_rate:
                            tax_nodet_rate = tax.amount
                        tax = account_tax_model.browse(
                            cr, uid, tax.parent_id.id)

                        if tax.amount > tax_rate:
                            tax_rate = tax.amount

                if invoice_tax.base_code_id.exclude_from_registries:
                    continue
                taxcode_base_id = invoice_tax.base_code_id.id
                taxcode_vat_id = invoice_tax.tax_code_id.id

                if tax_nature == 'FC':
                    sum_amounts['discarded'] += invoice.amount_total
                    continue
                if not invoice_tax.tax_code_id and not tax_nature:
                    raise orm.except_orm(
                        _(u'Error!'),
                        _(u'Invalid tax %s nature for invoice %s') % (
                            invoice_tax.name,
                            invoice.number))
                if taxcode_base_id not in inv_line:
                    inv_line[taxcode_base_id] = {}
                    inv_line[taxcode_base_id]['amount_taxable'] = 0.0
                    inv_line[taxcode_base_id]['amount_tax'] = 0.0
                    inv_line[taxcode_base_id]['amount_total'] = 0.0
                    inv_line[taxcode_base_id]['tax_vat_id'] = taxcode_vat_id
                    inv_line[taxcode_base_id]['tax_rate'] = tax_rate
                    inv_line[taxcode_base_id]['tax_nodet_rate'] = tax_nodet_rate
                    inv_line[taxcode_base_id]['tax_nature'] = tax_nature
                    inv_line[taxcode_base_id]['tax_payability'] = tax_payability
                if tax_rate and not inv_line[taxcode_base_id]['tax_rate']:
                    inv_line[taxcode_base_id]['tax_rate'] = tax_rate
                if tax_nodet_rate and not inv_line[taxcode_base_id]['tax_nodet_rate']:
                    inv_line[taxcode_base_id]['tax_nodet_rate'] = tax_nodet_rate
                if tax_payability and not inv_line[taxcode_base_id]['tax_payability']:
                    inv_line[taxcode_base_id]['tax_payability'] = tax_payability
                inv_line[taxcode_base_id]['amount_taxable'] += tax_dict['base']
                inv_line[taxcode_base_id]['amount_tax'] += tax_dict['amount']
                inv_line[taxcode_base_id]['amount_total'] += round(tax_dict['base'] + tax_dict['amount'], 2)
                if invoice.type[-7:] == '_refund':
                    sum_amounts['taxable'] -= tax_dict['base']
                    sum_amounts['tax'] -= tax_dict['amount']
                    sum_amounts['total'] -= round(tax_dict['base'] + tax_dict['amount'], 2)
                else:
                    sum_amounts['taxable'] += tax_dict['base']
                    sum_amounts['tax'] += tax_dict['amount']
                    sum_amounts['total'] += round(tax_dict['base'] + tax_dict['amount'], 2)
            if inv_line:
                comm_lines[invoice.id] = {}
                comm_lines[invoice.id]['partner_id'] = invoice.partner_id.id
                comm_lines[invoice.id]['taxes'] = inv_line
        return comm_lines, sum_amounts

    def load_DTE_DTR(self, cr, uid, commitment, commitment_line_model,
                     dte_dtr_id, context=None):
        journal_model = self.pool['account.journal']

        if release.major_version == '6.1':
            exclude_journal_ids = []
            fiscal_position_model = self.pool['account.fiscal.position']
            fiscal_position_ids = fiscal_position_model.search(cr, uid, [('journal_auto_invoice_id', '!=', False)], context=context)
            for fiscal_position in fiscal_position_model.browse(cr, uid, fiscal_position_ids, context):
                exclude_journal_ids.append(fiscal_position.journal_auto_invoice_id.id)
        else:
            exclude_journal_ids = journal_model.search(
                cr, uid, [('rev_charge', '=', True)])

        period_ids = [x.id for x in commitment.period_ids]
        company_id = commitment.company_id.id
        # tax_tree = self.build_tax_tree(cr, uid, company_id, context)
        where = [('company_id', '=', company_id),
                 ('period_id', 'in', period_ids),
                 ('journal_id', 'not in', exclude_journal_ids),
                 ('state', 'in', ('open', 'paid'))]
        if dte_dtr_id == 'DTE':
            where.append(('type', 'in', ['out_invoice', 'out_refund']))
        elif dte_dtr_id == 'DTR':
            where.append(('type', 'in', ['in_invoice', 'in_refund']))
        else:
            return

        fatturapa_attachment = False
        for period in commitment.period_ids:
            if period.fiscalyear_id and period.fiscalyear_id.name > '2018':
                fatturapa_attachment = True
                continue

        if fatturapa_attachment:
            country_ids = self.pool['res.country'].search(cr, uid, [('code', '=', 'IT')], context=context)
            where.append(('partner_id.country', 'not in', country_ids))
            if dte_dtr_id == 'DTE':
                where.append(('fatturapa_attachment_out_id', '=', False))
            elif dte_dtr_id == 'DTR':
                where.append(('fatturapa_attachment_in_id', '=', False))

        comm_lines, sum_amounts = self.load_invoices(
            cr, uid, commitment, commitment_line_model,
            dte_dtr_id, where, {}, context)
        if comm_lines:
            for line_id in commitment_line_model.search(
                cr, uid, [('commitment_id', '=', commitment.id),
                          ('invoice_id', 'not in', comm_lines.keys()), ], context=context):
                commitment_line_model.unlink(cr, uid, [line_id], context)
        for invoice_id in comm_lines:
            for line_id in commitment_line_model.search(
                cr, uid, [('commitment_id', '=', commitment.id),
                          ('invoice_id', '=', invoice_id),
                          ('tax_id', 'not in', comm_lines[
                              invoice_id]['taxes'].keys()),
                          ]):
                commitment_line_model.unlink(cr, uid, [line_id])
            for tax_id in comm_lines[invoice_id]['taxes']:
                line = {'commitment_id': commitment.id,
                        'invoice_id': invoice_id,
                        'tax_id': tax_id,
                        'partner_id': comm_lines[invoice_id]['partner_id'],
                        }
                for f in ('amount_total',
                          'amount_taxable',
                          'amount_tax',
                          'tax_vat_id',
                          'tax_rate',
                          'tax_nodet_rate',
                          'tax_nature',
                          'tax_payability',
                          ):
                    line[f] = comm_lines[invoice_id]['taxes'][tax_id][f]

                ids = commitment_line_model.search(
                    cr, uid, [('commitment_id', '=', commitment.id),
                              ('invoice_id', '=', invoice_id),
                              ('tax_id', '=', tax_id), ])
                if ids:
                    commitment_line_model.write(cr, uid, ids, line, context)
                else:
                    commitment_line_model.create(cr, uid, line, context)
        return sum_amounts

    def load_DTE(self, cr, uid, commitment, context=None):
        """Read all sale invoices in periods"""
        context = context or {}
        commitment_DTE_line_model = self.pool['account.vat.communication.dte.line']
        sum_amounts = self.load_DTE_DTR(
            cr, uid, commitment, commitment_DTE_line_model, 'DTE', context)
        return sum_amounts

    def load_DTR(self, cr, uid, commitment, context=None):
        """Read all purchase invoices in periods"""
        context = context or {}
        commitment_DTR_line_model = self.pool['account.vat.communication.dtr.line']
        sum_amounts = self.load_DTE_DTR(
            cr, uid, commitment, commitment_DTR_line_model, 'DTR', context)
        return sum_amounts

    def compute_amounts(self, cr, uid, ids, context=None):
        context = {} if context is None else context

        for commitment in self.browse(cr, uid, ids, context):
            dte_sum_amounts = self.load_DTE(cr, uid, commitment, context)
            dtr_sum_amounts = self.load_DTR(cr, uid, commitment, context)
            vals = {}
            for t in ('total', 'taxable', 'tax', 'discarded'):
                f = 'dte_amount_' + t
                vals[f] = dte_sum_amounts[t]
                f = 'dtr_amount_' + t
                vals[f] = dtr_sum_amounts[t]
            self.write(cr, uid, [commitment.id], vals, context)
        return True

    def onchange_fiscalcode(self, cr, uid, ids, fiscalcode, name,
                            country_id=None, context=None):
        name = name or 'fiscalcode'
        if fiscalcode:
            country_model = self.pool.get('res.country')
            if country_id and country_model.browse(
                    cr, uid, country_id, context).code != 'IT':
                return {'value': {name: fiscalcode,
                                  'individual': True}}
            elif len(fiscalcode) == 11:
                res_partner_model = self.pool.get('res.partner')
                chk = res_partner_model.simple_vat_check(
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

    #
    # INTERNAL INTERFACE TO XML EXPORT CODE
    #
    def get_xml_fattura_header(self, cr, uid, commitment, dte_dtr_id,
                               context=None):
        """Return DatiFatturaHeader: may be empty"""
        res = {}
        if commitment.codice_carica and commitment.soggetto_codice_fiscale:
            res['xml_CodiceFiscale'] = commitment.soggetto_codice_fiscale
            res['xml_Carica'] = commitment.codice_carica
        return res

    def get_xml_company(
            self, cr, uid, commitment, dte_dtr_id, context=None):
        """Return data of CessionarioCommittente or CedentePrestatore
        which referers to current company.
        This function is pair to get_xml_cessionario_cedente which returns
        customer or supplier data"""
        line_model = self.pool['account.vat.communication.line']
        res = line_model._dati_partner(
            cr, uid, commitment.company_id.partner_id, None, context)
        if res['xml_IdPaese'] != 'IT':
            raise orm.except_orm(
                _('Error!'),
                _('Missed company VAT number'))
        return res

    def get_partner_list(self, cr, uid, commitment, dte_dtr_id,
                         context=None):
        """Return list of partner_id in communication by commitment_id
        This function has to be used for CessionarioCommittente or
        CedentePrestatore iteration"""
        if dte_dtr_id != 'DTE' and dte_dtr_id != 'DTR':
            raise orm.except_orm(
                _('Error!'),
                _('Internal error: no DTE neither DTR selected'))
        model_name = 'account.vat.communication.%s.line' % dte_dtr_id.lower()
        table_name = model_name.replace('.', '_')
        sql = 'SELECT DISTINCT partner_id FROM %s WHERE commitment_id = %d' % \
            (table_name, commitment.id)
        cr.execute(sql)
        ids = []
        for rec in cr.fetchall():
            ids.append(rec[0])
        return ids

    def get_xml_cessionario_cedente(self, cr, uid, commitment, partner_id,
                                    dte_dtr_id, context=None):
        """Return data of CessionarioCommittente or CedentePrestatore
        This function has to be used as result of every iteration of
        get_partner_list"""
        commitment_line_model = self.pool['account.vat.communication.line']
        res_partner_model = self.pool['res.partner']
        partner = res_partner_model.browse(cr, uid, partner_id)
        return commitment_line_model._dati_partner(cr, uid, partner,
                                                   None, context)

    def get_invoice_list(self, cr, uid, commitment, partner_id, dte_dtr_id,
                         context=None):
        """Return list of invoices in communication
        by partner_id and commitment_id.
        This function has to be used for CessionarioCommittente or
        CedentePrestatore sub-iteration"""
        if dte_dtr_id != 'DTE' and dte_dtr_id != 'DTR':
            raise orm.except_orm(
                _('Error!'),
                _('Internal error: no DTE neither DTR selected'))
        model_name = 'account.vat.communication.%s.line' % dte_dtr_id.lower()
        table_name = model_name.replace('.', '_')
        sql = '''SELECT DISTINCT invoice_id FROM %s
                        WHERE commitment_id = %d and partner_id = %d''' % \
            (table_name, commitment.id, partner_id)
        cr.execute(sql)
        ids = []
        for rec in cr.fetchall():
            ids.append(rec[0])
        return ids

    def get_xml_invoice(self, cr, uid, commitment, invoice_id,
                        dte_dtr_id, context=None):
        """Return data of Invoice.
        This function has to be used as result of every iteration of
        get_invoice_list"""
        account_invoice_model = self.pool['account.invoice']
        invoice = account_invoice_model.browse(cr, uid, invoice_id)
        res = {}
        res['xml_TipoDocumento'] = self.pool[
            'account.vat.communication.line']._tipodocumento(cr, uid, invoice,
                                                             context)
        res['xml_Data'] = invoice.date_invoice
        if invoice.type in ('in_invoice', 'in_refund'):
            if not invoice.supplier_invoice_number:
                raise orm.except_orm(
                    _('Error!'),
                    _('Missed supplier invoice number %s') % (invoice.number))
            res['xml_Numero'] = invoice.supplier_invoice_number[-20:]
            res['xml_DataRegistrazione'] = invoice.registration_date
        else:
            res['xml_Numero'] = invoice.number[:20]
        return res

    def get_riepilogo_list(self, cr, uid, commitment, invoice_id,
                           dte_dtr_id, context=None):
        """Return list of tax lines of invoice in communication
        by invoice_id and commitment.id.
        This function has to be used for CessionarioCommittente or
        CedentePrestatore sub-sub-iteration"""
        if dte_dtr_id != 'DTE' and dte_dtr_id != 'DTR':
            raise orm.except_orm(
                _('Error!'),
                _('Internal error: no DTE neither DTR selected'))
        model_name = 'account.vat.communication.%s.line' % dte_dtr_id.lower()
        line_model = self.pool[model_name]
        ids = line_model.search(
            cr, uid, [
                ('commitment_id', '=', commitment.id),
                ('invoice_id', '=', invoice_id)
            ])
        return ids

    def get_xml_riepilogo(self, cr, uid, commitment, line_id,
                          dte_dtr_id, context=None):
        """Return data of tax invoice line.
        This function has to be used as result of every iteration of
        get_riepilogo_list"""
        commitment_line_model = self.pool['account.vat.communication.line']
        model_name = 'account.vat.communication.%s.line' % dte_dtr_id.lower()
        line_model = self.pool[model_name]
        commitment_line = line_model.browse(cr, uid, line_id)
        return commitment_line_model._dati_line(
            cr, uid, commitment_line, {'xml': True}, context)


class commitment_line(orm.AbstractModel):
    _name = 'account.vat.communication.line'

    def _xml_dati_partner(self, cr, uid, ids, fname, args, context=None):
        res = {}
        ctx = context.copy()
        ctx['no_except'] = True
        for line in self.browse(cr, uid, ids, context=ctx):
            fields = self._dati_partner(cr, uid, line.partner_id, args, context=ctx)
            if not line.tax_rate and not line.tax_nature:
                fields['xml_Error'] += _('No tax Nature')
            elif line.tax_nature and line.tax_nature == 'N6' and not line.tax_rate:
                if line.invoice_id.type in ('in_invoice', 'in_refund'):
                    fields['xml_Error'] += u"""la natura N6 -
        Reverse Charge è compatibile solo con l'aliquota diversa da 0 per le
        fatture ricevute"""
            result = {}
            for f in fname:
                if fields.get(f, ''):
                    result[f] = fields[f]
            res[line.id] = result
        return res

    def _xml_dati_lines(self, cr, uid, ids, fname, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = self._dati_line(cr, uid, line, args, context=context)
        return res

    def _xml_tipodocumento(self, cr, uid, ids, fname, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = self._tipodocumento(cr, uid, line.invoice_id, context=context)
        return res

    def _get_error(self, error, context):
        if context.get('no_except', False):
            return error
        else:
            raise orm.except_orm(_('Error!'), error)
        return False

    def _dati_partner(self, cr, uid, partner, args, context=None):
        if release.major_version == '6.1':
            address_id = self.pool['res.partner'].address_get(
                cr, uid, [partner.id])['default']
            address = self.pool['res.partner.address'].browse(
                cr, uid, address_id, context)
        else:
            address = partner

        res = {'xml_Error': ''}

        if partner.vat:
            vat = partner.vat.replace(' ', '').upper()
            res['xml_IdPaese'] = vat and vat[0:2] or ''
            res['xml_IdCodice'] = vat and vat[2:] or ''
        else:
            res['xml_IdPaese'] = partner.country and partner.country.code or 'OO'
            res['xml_IdCodice'] = '99999999999' or ''

        res['xml_Nazione'] = address.country_id.code or res.get('xml_IdPaese')
        if not res.get('xml_Nazione'):
            self._get_error(_('Unknow country of %s') % partner.name, context)

        if partner.individual and partner.fiscalcode:
            r = self.pool['account.vat.communication'].onchange_fiscalcode(
                cr, uid, partner.id,
                partner.fiscalcode, None,
                country_id=partner.country,
                context=context)
            if 'warning' in r:
                res['xml_Error'] += self._get_error(_('Invalid fiscalcode of %s') % partner.name, context)

            res['xml_CodiceFiscale'] = partner.fiscalcode.upper().replace(' ', '')
        elif res.get('xml_IdPaese', '') == 'IT':
            # res['xml_CodiceFiscale'] = res['xml_IdCodice']
            pass
        elif not res.get('xml_IdCodice', False):
            res['xml_CodiceFiscale'] = '99999999999'
        if res.get('xml_CodiceFiscale'):
            if len(res['xml_CodiceFiscale']) not in [11, 16]:
                res['xml_Error'] += self._get_error(_('Invalid fiscalcode lenght of %s') % partner.name, context)

        if partner.individual and not partner.vat:
            if release.major_version == '6.1':
                if partner.fiscalcode_firstname and partner.fiscalcode_surname:
                    res['xml_Nome'] = partner.fiscalcode_firstname
                    res['xml_Cognome'] = partner.fiscalcode_surname
                else:
                    res['xml_Denominazione'] = partner.name[:80]
            else:
                res['xml_Nome'] = partner.firstname
                res['xml_Cognome'] = partner.lastname
            if not res.get('xml_Cognome') or not res.get('xml_Nome'):
                res['xml_Error'] += self._get_error(_('Invalid First or Last name %s') % (partner.name), context)
        else:
            res['xml_Denominazione'] = partner.name
            if not partner.vat and \
                    (res['xml_Nazione'] == 'IT' or
                     res['xml_Nazione'] in EU_COUNTRIES):
                self._get_error(_('Partner %s without VAT number') % (partner.name), context)

        res['xml_Nazione'] = address.country_id.code or res.get('xml_IdPaese', False)

        if not res['xml_Nazione']:
            res['xml_Error'] += self._get_error(('Impossible determine country code for partner {}').format(partner.name), context)
        if address.street or address.street2:
            if address.street:
                res['xml_Indirizzo'] = address.street.replace(u"'", '').replace(u"’", '')
            else:
                res['xml_Indirizzo'] = address.street2.replace(u"'", '').replace(u"’", '')
        else:
            if context.get('no_except', False):
                res['xml_Error'] += self._get_error(_('Partner %s without street on address') % (partner.name), context)

        if res.get('xml_IdPaese', '') == 'IT':
            if address.zip:
                res['xml_CAP'] = address.zip.replace('x', '0').replace('%', '0').replace(' ', '')
            if len(res.get('xml_CAP', '')) != 5 or not res.get('xml_CAP', '').isdigit():
                res['xml_Error'] += self._get_error(_('Partner %s has wrong zip code') % (partner.name), context)
        res['xml_Comune'] = address.city or ' '
        if not address.city:
            res['xml_Error'] += self._get_error(_('Partner %s without city on address') % (partner.name), context)
        if res['xml_Nazione'] == 'IT':
            if release.major_version == '6.1':
                res['xml_Provincia'] = address.province.code
            else:
                res['xml_Provincia'] = partner.state_id.code
            if not res['xml_Provincia']:
                del res['xml_Provincia']
                res['xml_Error'] += self._get_error(_('Partner %s without province on address') % (
                        partner.name), context)
        return res

    def _dati_line(self, cr, uid, line, args, context=None):
        res = {
            'xml_ImponibileImporto': abs(line.amount_taxable),
            'xml_Imposta': abs(line.amount_tax),
            'xml_Aliquota': line.tax_rate * 100,
            'xml_Detraibile': 100.0 - line.tax_nodet_rate * 100
        }

        if args and args.get('xml', False):
            # Load data during export xml
            if res['xml_Detraibile'] == 0:
                res['xml_Deducibile'] = "SI"
                del res['xml_Detraibile']
            if line.tax_nature:
                res['xml_Natura'] = line.tax_nature
            if line.tax_payability:
                res['xml_EsigibilitaIVA'] = line.tax_payability
        else:
            # Data to line for displaying
            res['xml_Natura'] = line.tax_nature
        return res

    def _tipodocumento(self, cr, uid, invoice, context=None):
        doctype = invoice.type
        country_code = self.pool['account.vat.communication'].get_country_code(
            cr, uid, invoice.partner_id)
        if doctype == 'out_invoice' and \
                not invoice.partner_id.vat and \
                not invoice.partner_id.fiscalcode:
            if invoice.amount_total >= 0:
                return 'TD07'
            else:
                return 'TD08'
        elif doctype == 'out_refund' and \
                not invoice.partner_id.vat and \
                not invoice.partner_id.fiscalcode:
            return 'TD08'
        elif country_code != 'IT' and country_code in EU_COUNTRIES and doctype == 'in_invoice':
            for line in invoice.invoice_line:
                if line.product_id and line.product_id.type == 'service':
                    return 'TD11'
                return 'TD10'
        elif doctype in ('out_invoice', 'in_invoice'):
            if invoice.amount_total >= 0:
                return 'TD01'
            else:
                return 'TD04'
        elif doctype in ('out_refund', 'in_refund'):
            return 'TD04'
        else:
            raise orm.except_orm(
                _('Error!'),
                _('Invalid type %s (%s) for invoice %s') % (doctype,
                                                            country_code,
                                                            invoice.number))

    _columns = {
        'xml_Error': fields.function(
            _xml_dati_partner,
            string="Error",
            type="char",
            multi=True,
            store=False,
            select=True,
            readonly=True
        ),
        'xml_IdPaese': fields.function(
            _xml_dati_partner,
            string="Country",
            type="char",
            multi=True,
            store=False,
            select=True,
            readonly=True),
        'xml_IdCodice': fields.function(
            _xml_dati_partner,
            string="VAT number",
            type="char",
            multi=True,
            store=False,
            select=True,
            readonly=True),
        'xml_CodiceFiscale': fields.function(
            _xml_dati_partner,
            string="Fiscalcode",
            type="char",
            multi=True,
            store=False,
            select=True,
            readonly=True),
        'xml_TipoDocumento': fields.function(
            _xml_tipodocumento,
            string="Document type",
            help="Values: TD01=invoice, TD04=refund",
            type="char",
            store=False,
            select=True,
            readonly=True),
        'xml_ImponibileImporto': fields.function(
            _xml_dati_lines,
            string="Taxable",
            type="float",
            multi='xml_dati_line',
            store=False,
            select=True,
            readonly=True),
        'xml_Imposta': fields.function(
            _xml_dati_lines,
            string="Tax",
            type="float",
            multi='xml_dati_line',
            store=False,
            select=True,
            readonly=True),
        'xml_Aliquota': fields.function(
            _xml_dati_lines,
            string="Tax rate",
            type="float",
            multi='xml_dati_line',
            store=False,
            select=True,
            readonly=True),
        'xml_Detraibile': fields.function(
            _xml_dati_lines,
            string="Tax deductible",
            type="float",
            multi='xml_dati_line',
            store=False,
            select=True,
            readonly=True),
        'xml_Natura': fields.function(
            _xml_dati_lines,
            string="Tax type",
            type="char",
            multi='xml_dati_line',
            store=False,
            select=True,
            readonly=True),
    }


class commitment_DTE_line(orm.Model):
    _name = 'account.vat.communication.dte.line'
    _inherit = 'account.vat.communication.line'

    _columns = {
        'commitment_id': fields.many2one(
            'account.vat.communication', 'VAT commitment'),
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice'),
        'tax_id': fields.many2one(
            'account.tax.code', 'VAT code'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            readony=True),
        'tax_vat_id': fields.many2one(
            'account.tax.code', 'VAT code',
            readony=True),
        'tax_rate': fields.float(
            'VAT rate',
            readony=True),
        'tax_nodet_rate': fields.float(
            'VAT non deductible rate',
            readony=True),
        'tax_nature': fields.char(
            'Non taxable nature',
            readony=True),
        'tax_payability': fields.char(
            'VAT payability',
            readony=True),
        'amount_total': fields.float(
            'Amount', digits_compute=dp.get_precision('Account')),
        'amount_taxable': fields.float(
            'Taxable amount', digits_compute=dp.get_precision('Account')),
        'amount_tax': fields.float(
            'Tax amount', digits_compute=dp.get_precision('Account')),
    }


class commitment_DTR_line(orm.Model):
    _name = 'account.vat.communication.dtr.line'
    _inherit = 'account.vat.communication.line'

    _columns = {
        'commitment_id': fields.many2one(
            'account.vat.communication', 'VAT commitment'),
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice'),
        'tax_id': fields.many2one(
            'account.tax.code', 'VAT code'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            readony=True),
        'tax_vat_id': fields.many2one(
            'account.tax.code', 'VAT code',
            readony=True),
        'tax_rate': fields.float(
            'VAT rate',
            readony=True),
        'tax_nodet_rate': fields.float(
            'VAT non deductible rate',
            readony=True),
        'tax_nature': fields.char(
            'Non taxable nature',
            readony=True),
        'tax_payability': fields.char(
            'VAT payability',
            readony=True),
        'amount_total': fields.float(
            'Amount', digits_compute=dp.get_precision('Account')),
        'amount_taxable': fields.float(
            'Taxable amount', digits_compute=dp.get_precision('Account')),
        'amount_tax': fields.float(
            'Tax amount', digits_compute=dp.get_precision('Account')),
    }


class AccountPeriod(orm.Model):
    _inherit = "account.period"
    _columns = {
        'vat_commitment_id': fields.many2one(
            'account.vat.communication', "VAT commitment"),
    }
