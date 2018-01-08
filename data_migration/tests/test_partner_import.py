# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

"""
$ workon OE_61
$ export PYTHONPATH=/Users/andrei/Programming/lp/OpenERP_6.1/server_61/:/Users/andrei/Programming/lp/openerp-command/
$ export PATH=/Users/andrei/Programming/lp/OpenERP_6.1/server_61/:/Users/andrei/Programming/lp/openerp-command/:$PATH
$ oe run-tests -m data_migration -d <database_name> --addons /Users/andrei/Programming/lp/OpenERP_6.1/aeroo/:/Users/andrei/Programming/lp/LibrERP/:/Users/andrei/Programming/lp/OpenERP_6.1/addons_61

"""

from openerp.tests.common import TransactionCase
from openerp.addons.data_migration.utils.partner_importer import ImportFile
import unittest2


class TestOmnitronPartnerImport(TransactionCase):
    class OmnitronConfig(object):
        DEBUG = True
        HEADER_CUSTOMER = (
            'IDContatto', 'CodiceContatto',
            'RagioneSociale',
            'IndirizzoSedeLegale', 'CAPSedeLegale', 'LocalitaSedeLegale', 'ProvinciaSedeLegale',
            'RagioneSocialeOperativo',
            'IndirizzoOperativo', 'CAPOperativo', 'LocalitaOperativo', 'ProvinciaOperativo',
            'Telefono', 'Fax', 'Email', 'Web', 'Cellulare',
            'PartitaIVA', 'CodiceFiscale', 'IDPagamento',
            'Pagamento', 'BancaAppoggio', 'ABI', 'CAB', 'ContoCorrente',
            'IDCorriere', 'Corriere', 'IDTrasporto', 'Trasporto',
            'CodiceMerceologico', 'CodiceDivisione',
            'Commenti', 'IDNazione', 'IDRegione', 'IDRespAgente', 'IDTipoCliente',
            'ClienteFornitore', 'Appartenenza',
            'IVAAna', 'AnnoAna', 'IBAN', 'EMailFatture', 'Nazione', 'Valuta'
        )

        COLUMNS = """
                none, code, 
                name,
                street_default, zip_default, city_default, province_default,
                name_delivery,
                street_delivery, zip_delivery, city_delivery, province_delivery,
                phone_default, fax_default, email_default, web_default, mobile_default,
                vat, fiscalcode, none2,
                payment_term, bank, abi, cab, account,
                none4, none5, none6, none7, 
                none8, none9, 
                comment, none10, none11, none12, none13,
                client_supplier, none14,
                none15, none16, iban, email_invoice, country_name, currency
            """
        ADDRESS_TYPE = ('default', 'delivery')
        REQUIRED = ['name']
        PARTNER_SEARCH = ['vat', 'code', 'name']
        PARTNER_UNIQUE_OFFICE_CODE = True

    class ImportSettings(object):
        state = 'end'

        # Data of file, in code BASE64
        content_base64 = False
        file_name = 'Omnitron'
        format = 'FormatOmnitron'
        progress_indicator = 0
        strict = False
        partner_type = 'customer'
        update_on_code = False
        partner_template_id = False
        _model = 'res.partner'

    def setUp(self):
        super(TestOmnitronPartnerImport, self).setUp()
        self.import_model = ImportFile(self.cr, self.uid, [False], context={})
        self.import_model.setup(self.ImportSettings, self.OmnitronConfig)
        self.import_model.processed_lines = 0

    def test_import(self):
        test_values = [
            {
                'request': [
                    '18882', '0018882', '2EMMEDI GROUP s.r.l.',
                    'Vicolo C. Colombo, 15', '31032', 'CASALE SUL SILE', 'TV', '2EMMEDI GROUP s.r.l.',
                    'Vicolo C. Colombo, 15', '31032', 'CASALE SUL SILE', 'TV', '0422 821072', '0422 821083',
                    '2emmedigroup@libero.it', '\N', '\N', '04722550268', '04722550268', 3, 'ALL ORDINE',
                    "BANCA POPOLARE DELL'ALTO ADIGE - AG. MARGHERA (VE)", '\N', '\N', '\N', 221,
                    'A CURA DESTINATARIO', 3, 'ASSEGNATO', 4, 'Water', False, 5, 26, 1, 1005, 0, 'BM-PD',
                    22, 2016, 'IT68H0585602001130571297880', '\N', 'ITALIA', 'EURO'
                ],
                'reply': {},
                'country_id': 110
            },
            {
                'request': [
                    '18180', '0018180', 'AL-GHADEER TRADING EST.',
                    'Khalidia Tower - Tenth floor - office no.41015', '11417', 'Riyadh', '\N',
                    'AL-GHADEER TRADING EST.', 'Khalidia Tower - Tenth floor - office no.41015', '11417',
                    'Riyadh', '\N', '009661 4091100', '009661 4093300', '\N', '\N', '00966 506238957', '\N',
                    '\N', 3, "ALL'ORDINE", '\N', '\N', '\N', '\N', 0, '\N', 0, '\N', 0, False,
                    'VENDITA/ESPORTAZIONE EXTRA UNIONE EUROPEA  -  Esente IVA ai sensi art. 8 COMMA 1 DPR 633/72',
                    1025, 1019, 1, 0, 0, 'BM-PD', 0, 2012, '\N', '\N', 'ARABIA SAUDITA', 'EURO'
                ],
                'country_id': False
            }
        ]

        for values in test_values:
            record = self.import_model.Record._make([self.import_model.toStr(value) for value in values['request']])
            print record

            vals_partner, country_id = self.import_model.collect_values(self.cr, self.uid, record)
            print vals_partner

            print country_id
            self.assertEqual(values['country_id'], country_id, 'Wrong country')


if __name__ == '__main__':
    unittest2.main()
