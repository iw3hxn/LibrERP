# -*- coding: utf-8 -*-
#    Copyright (C) 2017    SHS-AV s.r.l. <https://www.zeroincombenze.it>
#    Copyright (C) 2017    Didotech srl <http://www.didotech.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# [2017: SHS-AV s.r.l.] First version
#
from openerp.osv import fields, orm
from openerp.tools.translate import _
# from openerp import release
import logging
_logger = logging.getLogger(__name__)
try:
    from unidecode import unidecode
    from openerp.addons.l10n_it_ade.bindings.dati_fattura_v_2_0 import (
        DatiFattura,
        VersioneType,
        DatiFatturaHeaderType,
        DichiaranteType,
        CodiceFiscaleType,
        DTEType,
        CedentePrestatoreDTEType,
        IdentificativiFiscaliType,
        IdentificativiFiscaliITType,
        IdFiscaleITType,
        IdFiscaleType,
        CessionarioCommittenteDTEType,
        AltriDatiIdentificativiNoSedeType,
        AltriDatiIdentificativiNoCAPType,
        IdentificativiFiscaliNoIVAType,
        IndirizzoType,
        IndirizzoNoCAPType,
        # RettificaType,
        DatiFatturaBodyDTEType,
        DatiGeneraliType,
        DatiRiepilogoType,
        DatiIVAType,
        DTRType,
        CessionarioCommittenteDTRType,
        CedentePrestatoreDTRType,
        DatiFatturaBodyDTRType,
        DatiGeneraliDTRType,
    )
    #   ANNType)
except ImportError as err:
    _logger.debug(err)

_logger.setLevel(logging.DEBUG)

VERSIONE = 'DAT20'


class WizardVatCommunication(orm.TransientModel):
    _name = "wizard.vat.communication"

    _columns = {
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 32, readonly=True),
        'state': fields.selection((
            ('create', 'create'),  # choose
            ('get', 'get'),  # get the file
        )),
        'target': fields.char('Customers/Suppliers', 4, readonly=True),
    }

    _defaults = {
        'state': lambda *a: 'create',
    }

    def str60Latin(self, s):
        # t = s.encode('latin-1', 'ignore')
        return unidecode(s)[:60]

    def str80Latin(self, s):
        return unidecode(s)[:80]

    def get_dati_fattura_header(self, cr, uid,
                                commitment_model, commitment, context=None):
        context = context or {}
        fields = commitment_model.get_xml_fattura_header(
            cr, uid, commitment, context)
        header = (DatiFatturaHeaderType())
        if 'xml_CodiceFiscale' in fields:
            header.Dichiarante = (DichiaranteType())
            header.Dichiarante.Carica = fields['xml_Carica']
            header.Dichiarante.CodiceFiscale = CodiceFiscaleType(
                fields['xml_CodiceFiscale'])
        return header

    def get_sede(self, cr, uid, fields, dte_dtr_id, selector, context=None):
        if dte_dtr_id == 'DTE':
            if selector == 'company':
                sede = (IndirizzoType())
            elif selector == 'customer':
                sede = (IndirizzoNoCAPType())
            elif selector == 'supplier':
                sede = (IndirizzoType())
            else:
                raise orm.except_orm(
                    _('Error!'),
                    _('Internal error: invalid partner selector'))
        else:
            if selector == 'company':
                sede = (IndirizzoType())
            elif selector == 'customer':
                sede = (IndirizzoNoCAPType())
            elif selector == 'supplier':
                sede = (IndirizzoNoCAPType())
            else:
                raise orm.except_orm(
                    _('Error!'),
                    _('Internal error: invalid partner selector'))

        if fields.get('xml_Nazione'):
            sede.Nazione = fields['xml_Nazione']
        else:
            raise orm.except_orm(
                _('Error!'),
                _('Unknow country of %s %s %S' %
                  (fields.get('xml_Denominazione'),
                   fields.get('xml_Nome'),
                   fields.get('xml_Cognome'))))

        if fields.get('xml_Indirizzo'):
            sede.Indirizzo = self.str60Latin(fields['xml_Indirizzo'])
        else:
            raise orm.except_orm(
                _('Error!'),
                _('Missed address %s %s %S' %
                  (fields.get('xml_Denominazione'),
                   fields.get('xml_Nome'),
                   fields.get('xml_Cognome'))))
        if fields.get('xml_Comune'):
            sede.Comune = self.str60Latin(fields['xml_Comune'])
        else:
            raise orm.except_orm(
                _('Error!'),
                _('Missed city %s %s %S' %
                  (fields.get('xml_Denominazione'),
                   fields.get('xml_Nome'),
                   fields.get('xml_Cognome'))))
        if fields.get('xml_CAP') and fields['xml_Nazione'] == 'IT':
            sede.CAP = fields['xml_CAP']
        elif selector == 'company':
            raise orm.except_orm(
                _('Error!'),
                _('Missed company zip code'))
        if fields.get('xml_Provincia') and fields['xml_Nazione'] == 'IT':
            sede.Provincia = fields['xml_Provincia']
        return sede

    def get_name(self, cr, uid, fields, dte_dtr_id, selector, context=None):
        if dte_dtr_id == 'DTE':
            if selector == 'company':
                AltriDatiIdentificativi = (AltriDatiIdentificativiNoSedeType())
            elif selector == 'customer' or selector == 'supplier':
                AltriDatiIdentificativi = (AltriDatiIdentificativiNoCAPType())
            else:
                raise orm.except_orm(
                    _('Error!'),
                    _('Internal error: invalid partner selector'))
        else:
            if selector == 'company':
                AltriDatiIdentificativi = (AltriDatiIdentificativiNoSedeType())
            elif selector == 'customer' or selector == 'supplier':
                AltriDatiIdentificativi = (AltriDatiIdentificativiNoCAPType())
            else:
                raise orm.except_orm(
                    _('Error!'),
                    _('Internal error: invalid partner selector'))

        if 'xml_Denominazione' in fields:
            AltriDatiIdentificativi.Denominazione = self.str80Latin(
                fields['xml_Denominazione'])
        else:
            AltriDatiIdentificativi.Nome = self.str60Latin(
                fields['xml_Nome'])
            AltriDatiIdentificativi.Cognome = self.str60Latin(
                fields['xml_Cognome'])
        AltriDatiIdentificativi.Sede = self.get_sede(
            cr, uid, fields, dte_dtr_id, selector, context=context)
        return AltriDatiIdentificativi

    def get_cedente_prestatore(self, cr, uid,
                               fields, dte_dtr_id,
                               context=None):

        if dte_dtr_id == 'DTE':
            CedentePrestatore = (CedentePrestatoreDTEType())
            CedentePrestatore.IdentificativiFiscali = (
                IdentificativiFiscaliITType())
            # Company VAT number must be present
            CedentePrestatore.IdentificativiFiscali.IdFiscaleIVA = (
                IdFiscaleITType())
            partner_type = 'company'
        elif dte_dtr_id == 'DTR':
            CedentePrestatore = (CedentePrestatoreDTRType())
            CedentePrestatore.IdentificativiFiscali = (
                IdentificativiFiscaliType())
            # Company VAT number must be present
            CedentePrestatore.IdentificativiFiscali.IdFiscaleIVA = (
                IdFiscaleType())
            partner_type = 'supplier'
        else:
            raise orm.except_orm(
                _('Error!'),
                _('Internal error: invalid partner selector'))

        if fields.get('xml_IdPaese') and fields.get('xml_IdCodice'):
            CedentePrestatore.IdentificativiFiscali.IdFiscaleIVA.\
                IdPaese = fields['xml_IdPaese']
            CedentePrestatore.IdentificativiFiscali.IdFiscaleIVA.\
                IdCodice = fields['xml_IdCodice']
        if fields.get('xml_CodiceFiscale'):
            CedentePrestatore.IdentificativiFiscali.CodiceFiscale = \
                CodiceFiscaleType(fields['xml_CodiceFiscale'])
        CedentePrestatore.AltriDatiIdentificativi = \
            self.get_name(cr, uid, fields, dte_dtr_id, partner_type, context)
        return CedentePrestatore

    def get_cessionario_committente(self, cr, uid,
                                    fields, dte_dtr_id,
                                    context=None):

        if dte_dtr_id == 'DTE':
            partner = (CessionarioCommittenteDTEType())
            partner_type = 'customer'
            partner.IdentificativiFiscali = (IdentificativiFiscaliNoIVAType())
        else:
            # DTR
            partner = (CessionarioCommittenteDTRType())
            partner_type = 'company'
            partner.IdentificativiFiscali = (IdentificativiFiscaliITType())

        if fields.get('xml_IdPaese') and fields.get('xml_IdCodice'):
            if dte_dtr_id == 'DTE':
                partner.IdentificativiFiscali.IdFiscaleIVA = (IdFiscaleType())
            else:
                partner.IdentificativiFiscali.IdFiscaleIVA = (
                    IdFiscaleITType())

            partner.IdentificativiFiscali.IdFiscaleIVA.\
                IdPaese = fields['xml_IdPaese']
            partner.IdentificativiFiscali.IdFiscaleIVA.\
                IdCodice = fields['xml_IdCodice']

            if fields.get('xml_IdPaese') == 'IT' and fields.get(
                    'xml_CodiceFiscale'):
                partner.IdentificativiFiscali.\
                    CodiceFiscale = CodiceFiscaleType(
                        fields['xml_CodiceFiscale'])
        else:
            partner.IdentificativiFiscali.CodiceFiscale = CodiceFiscaleType(
                fields['xml_CodiceFiscale'])
        # row 44: 2.2.2   <AltriDatiIdentificativi>
        partner.AltriDatiIdentificativi = \
            self.get_name(cr, uid, fields, dte_dtr_id, partner_type, context)
        return partner

    def get_dte_dtr(self, cr, uid,
                    commitment_model, commitment, dte_dtr_id, context=None):
        context = context or {}

        partners = []
        partner_ids = commitment_model.get_partner_list(
            cr, uid, commitment, dte_dtr_id, context)
        for partner_id in partner_ids:
            fields = commitment_model.get_xml_cessionario_cedente(
                cr, uid, commitment, partner_id, dte_dtr_id, context)

            # Missed mandatory data: skip record
            # if not fields.get('xml_IdPaese') and \
            #         not fields.get('xml_IdCodice') and \
            #         not fields.get('xml_CodiceFiscale', False):
            #     # Corrispettivi
            #     continue
            # TODO: StabileOrganizzazione
            # TODO: RappresentanteFiscale

            if dte_dtr_id == 'DTE':
                partner = self.get_cessionario_committente(
                    cr, uid, fields, dte_dtr_id, context)
            else:
                partner = self.get_cedente_prestatore(
                    cr, uid, fields, dte_dtr_id, context
                )

            invoices = []
            # Iterate over invoices of current partner
            invoice_ids = commitment_model.get_invoice_list(
                cr, uid, commitment, partner_id, dte_dtr_id, context)
            for invoice_id in invoice_ids:
                fields = commitment_model.get_xml_invoice(
                    cr, uid, commitment, invoice_id, dte_dtr_id, context)
                if dte_dtr_id == 'DTE':
                    invoice = (DatiFatturaBodyDTEType())
                    invoice.DatiGenerali = (DatiGeneraliType())
                else:
                    invoice = (DatiFatturaBodyDTRType())
                    invoice.DatiGenerali = (DatiGeneraliDTRType())

                invoice.DatiGenerali.TipoDocumento = fields[
                    'xml_TipoDocumento']
                invoice.DatiGenerali.Data = fields['xml_Data']
                invoice.DatiGenerali.Numero = fields['xml_Numero']
                if dte_dtr_id == 'DTR':
                    invoice.DatiGenerali.DataRegistrazione = fields[
                        'xml_DataRegistrazione']

                dati_riepilogo = []
                line_ids = commitment_model.get_riepilogo_list(
                    cr, uid, commitment, invoice_id, dte_dtr_id, context)
                for line_id in line_ids:
                    fields = commitment_model.get_xml_riepilogo(
                        cr, uid, commitment, line_id, dte_dtr_id, context)
                    riepilogo = (DatiRiepilogoType())
                    riepilogo.ImponibileImporto = '{:.2f}'.format(
                        fields['xml_ImponibileImporto'])
                    riepilogo.DatiIVA = (DatiIVAType())
                    riepilogo.DatiIVA.Imposta = '{:.2f}'.format(
                        fields['xml_Imposta'])
                    riepilogo.DatiIVA.Aliquota = '{:.2f}'.format(
                        fields['xml_Aliquota'])
                    if 'xml_Detraibile' in fields:
                        riepilogo.Detraibile = '{:.2f}'.format(
                            fields['xml_Detraibile'])
                    if 'xml_Deducibile' in fields:
                        riepilogo.Deducibile = fields['xml_Deducibile']
                    if 'xml_Natura' in fields:
                        riepilogo.Natura = fields['xml_Natura']
                    riepilogo.EsigibilitaIVA = fields['xml_EsigibilitaIVA']
                    dati_riepilogo.append(riepilogo)
                invoice.DatiRiepilogo = dati_riepilogo
                invoices.append(invoice)

            if dte_dtr_id == 'DTE':
                partner.DatiFatturaBodyDTE = invoices
            else:
                partner.DatiFatturaBodyDTR = invoices
            partners.append(partner)

        fields = commitment_model.get_xml_company(
            cr, uid, commitment, dte_dtr_id, context)
        if dte_dtr_id == 'DTE':
            dte = (DTEType())

            dte.CedentePrestatoreDTE = self.get_cedente_prestatore(
                cr, uid, fields, dte_dtr_id, context)
            dte.CessionarioCommittenteDTE = partners

            # dte.Rettifica = (RettificaType())

            return dte
        else:
            dtr = (DTRType())

            dtr.CessionarioCommittenteDTR = self.get_cessionario_committente(
                cr, uid, fields, dte_dtr_id, context
            )

            dtr.CedentePrestatoreDTR = partners

            # dtr.Rettifica = (RettificaType())

            return dtr

    def export_vat_communication_DTE(self, cr, uid, ids, context=None):
        context = context or {}
        context['dte_dtr_id'] = 'DTE'
        return self.export_vat_communication(cr, uid, ids, context)

    def export_vat_communication_DTR(self, cr, uid, ids, context=None):
        context = context or {}
        context['dte_dtr_id'] = 'DTR'
        return self.export_vat_communication(cr, uid, ids, context)

    def export_vat_communication(self, cr, uid, ids, context=None):
        context = context or {}
        dte_dtr_id = context.get('dte_dtr_id', 'DTE')
        commitment_model = self.pool['account.vat.communication']
        commitment_ids = context.get('active_ids', False)
        if commitment_ids:
            for commitment in commitment_model.browse(
                    cr, uid, commitment_ids, context=context):

                communication = DatiFattura()
                communication.versione = VersioneType(VERSIONE)
                communication.DatiFatturaHeader = self.get_dati_fattura_header(
                    cr, uid, commitment_model, commitment)

                if dte_dtr_id == 'DTE':
                    communication.DTE = self.get_dte_dtr(
                        cr, uid, commitment_model, commitment, dte_dtr_id,
                        context)
                elif dte_dtr_id == 'DTR':
                    communication.DTR = self.get_dte_dtr(
                        cr, uid, commitment_model, commitment, dte_dtr_id,
                        context)
                else:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Internal error: invalid partner selector'))
                # file_name = 'Comunicazine_IVA-{}.xml'.format(
                #     commitment.progressivo_telematico)
                progr_invio = commitment_model.set_progressivo_telematico(
                    cr, uid, commitment, context)
                file_name = 'IT%s_DF_%s.xml' % (
                    commitment.soggetto_codice_fiscale, progr_invio)
                vat_communication_xml = communication.toDOM().toprettyxml(
                    encoding="latin1")

                out = vat_communication_xml.encode("base64")

                attach_vals = {
                    'name': file_name,
                    'datas_fname': file_name,
                    'datas': out,
                    'res_model': 'account.vat.communication',
                    'res_id': commitment.id,
                    'type': 'binary',
                }

                self.pool['ir.attachment'].create(cr, uid, attach_vals)

                return self.write(
                    cr, uid, ids, {
                        'state': 'get',
                        'data': out,
                        'name': file_name,
                        'target': dte_dtr_id,
                    }, context=context
                )
