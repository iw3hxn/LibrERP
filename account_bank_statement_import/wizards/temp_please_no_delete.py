# -*- coding: utf-8 -*-
# © 2013-2017 Didotech srl (www.didotech.com)

# TODO This file is for inspirational purposes

import logging
import math
import threading
from collections import namedtuple
from datetime import datetime
from pprint import pprint
from openerp.addons.core_extended.file_manipulation import import_sheet

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

from openerp.addons.data_migration import settings
from openerp.osv import orm
from tools.translate import _
from psycopg2 import IntegrityError
from utils import Utils

try:
    import pooler
except ImportError:
    _logger.debug('Cannot import pooler')

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot import xlrd')

COUNTRY_CODES = settings.COUNTRY_CODES
DEBUG = settings.DEBUG

if DEBUG:
    import pdb

PROPERTY_REF_MAP = {
    'supplier': 'property_supplier_ref',
    'customer': 'property_customer_ref'
}

DONT_STOP_ON_WRONG_VAT = True

VAT_CODES = [
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI',
    'FR', 'DE', 'EL', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU',
    'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE',
    'GB'
]


class ImportFile(threading.Thread, Utils):
    def __init__(self, cr, uid, ids, context):
        # Inizializzazione superclasse
        threading.Thread.__init__(self)

        # Inizializzazione classe ImportPartner
        self.uid = uid
        self.dbname = cr.dbname
        self.start_time = datetime.now()
        self.pool = pooler.get_pool(cr.dbname)
        self.partner_obj = self.pool['res.partner']
        self.account_fiscal_position_obj = self.pool['account.fiscal.position']
        self.partner_template = self.pool['account.bank.statement.template']
        # Necessario creare un nuovo cursor per il thread, quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()

        self.bank_statement_import_id = ids[0]

        self.context = context
        self.error = []
        self.warning = []
        self.first_row = True

        # Contatori dei nuovi statement inseriti e aggiornati, vengono utilizzati per compilare il
        # rapporto alla terminazione del processo di import
        self.uo_new = 0
        self.updated = 0
        self.problems = 0

    def setup(self, import_settings=False, config=False):
        # Recupera il record dal database
        if import_settings:
            self.statementLineImportRecord = import_settings
        else:
            self.filedata_obj = self.pool['partner.import']
            self.statementLineImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.bank_statement_import_id,
                                                                      context=self.context)
        self.file_name = self.statementLineImportRecord.file_name.split('\\')[-1]
        self.strict = self.statementLineImportRecord.strict
        self.UPDATE_ON_CODE = self.statementLineImportRecord.update_on_code
        self.partner_template_id = self.statementLineImportRecord.partner_template_id

        if not config:
            config = getattr(settings, self.statementLineImportRecord.format)
        self.FORMAT = self.statementLineImportRecord.format
        self.HEADER = config.HEADER_CUSTOMER
        self.REQUIRED = config.REQUIRED
        self.PARTNER_SEARCH = config.PARTNER_SEARCH
        self.ADDRESS_TYPE = config.ADDRESS_TYPE
        self.PARTNER_UNIQUE_OFFICE_CODE = config.PARTNER_UNIQUE_OFFICE_CODE

        if not len(self.HEADER) == len(config.COLUMNS.split(',')):
            pprint(zip(self.HEADER, config.COLUMNS.split(',')))
            raise orm.except_orm('Error: wrong configuration!', 'The length of columns and headers must be the same')

        self.Record = namedtuple('Record', config.COLUMNS)
        # ===================================================

        self.partner_type = self.statementLineImportRecord.partner_type

    def run(self):
        self.setup()

        try:
            table, self.numberOfLines = import_sheet(self.file_name, self.statementLineImportRecord.content_text)
        except Exception as e:
            # Annulla le modifiche fatte
            self.cr.rollback()
            self.cr.commit()

            title = 'Import failed'
            message = "Errore nell'importazione del file %s" % self.file_name + "\nDettaglio:\n\n" + str(e)

            if DEBUG:
                # Debug
                _logger.debug(message)
                pdb.set_trace()
            self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.statementLineImportRecord)

        try:
            # Import account_bank_statement
            self.process(self.cr, self.uid, table)

            # Genera il report sull'importazione
            self.notify_import_result(self.cr, self.uid, 'Importazione Bank Statement', record=self.statementLineImportRecord)
        except Exception as e:
            # Annulla le modifiche fatte
            self.cr.rollback()
            self.cr.commit()

            title = "Import failed"
            message = u"Errore alla linea %s" % str(self.processed_lines) + "\nDettaglio:\n\n" + str(e)

            if DEBUG:
                raise e

            self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.statementLineImportRecord)

    def process(self, cr, uid, table, book_datemode=False):
        self.progressIndicator = 0

        notify_progress_step = (self.numberOfLines / 100) + 1

        for self.processed_lines, row_list in enumerate(table, start=1):
            # Import row
            if not self.import_row(cr, uid, row_list, book_datemode):
                self.problems += 1

            if (self.processed_lines % notify_progress_step) == 0:
                cr.commit()
                completed_quota = float(self.processed_lines) / float(self.numberOfLines)
                completed_percentage = math.trunc(completed_quota * 100)
                self.progressIndicator = completed_percentage
                self.updateProgressIndicator(cr, uid, self.bank_statement_import_id)

        self.progressIndicator = 100
        self.updateProgressIndicator(cr, uid, self.bank_statement_import_id)

        return True

    def _find_partner(self, cr, uid, vals_partner, context=None):
        partner_clone = set()
        for field in self.PARTNER_SEARCH:
            if vals_partner.get(field, False):
                _logger.info(u"Ricerca {0} = {1}".format(field, vals_partner[field]))
                partner_ids = self.partner_obj.search(cr, uid, [(field, '=', vals_partner[field])], context=self.context)
                if len(partner_ids) == 1:
                    if self.strict:
                        partner_clone.add(partner_ids[0])
                    else:
                        return partner_ids[0]
                elif len(partner_ids) > 1:
                    error = u'Riga {line}: Trovati più partner con {field} = {name}'.format(line=self.processed_lines, field=field, name=vals_partner[field])
                    _logger.debug(error)
                    self.error.append(error)
                    return -1

        if len(partner_clone) == 1:
            partner_id = partner_clone.pop()
            partner = self.partner_obj.browse(cr, uid, partner_id, context)
            for field in self.PARTNER_SEARCH:
                if vals_partner.get(field, False) and not vals_partner[field] == getattr(partner, field):
                    error = u'Riga {line}: Trovati più cloni del partner {name}'.format(line=self.processed_lines, name=partner.name)
                    _logger.debug(error)
                    self.error.append(error)
                    
                    error = u'Riga {line}: ----------------------------- {name} {vat}'.format(line=self.processed_lines, name=vals_partner['name'], vat=vals_partner.get('vat', ''))
                    _logger.debug(error)
                    self.error.append(error)
                    return -1
            return partner_id
        elif len(partner_clone) > 1:
            error = u'Riga {line}: Trovati più cloni del cliente {name}'.format(line=self.processed_lines, name=vals_partner['name'])
            _logger.debug(error)
            self.error.append(error)
            return -1
        return False

    def _country_by_code(self, cr, uid, code):
        if code in COUNTRY_CODES:
            code = COUNTRY_CODES[code]

        if len(code) == 2:
            country_ids = self.pool['res.country'].search(cr, uid, [('code', '=', code)], context=self.context)
        else:
            country_ids = False

        if country_ids:
            return country_ids[0]
        else:
            # search also for name
            country_ids = self.pool['res.country'].search(cr, uid, [('name', '=ilike', code)], context=self.context)
            if country_ids:
                return country_ids[0]
            else:
                return False


    def collect_values(self, cr, uid, record):
        self.first_row = False

        for field in self.REQUIRED:
            if not getattr(record, field):
                error = u"Riga {0}: Manca il valore della {1}. La riga viene ignorata.".format(self.processed_lines, field)
                _logger.debug(error)
                self.error.append(error)
                return False

        if self.FORMAT == 'FormatOmnitron':
            if record.client_supplier == u'1':
                self.partner_type = 'supplier'
            else:
                self.partner_type = 'customer'

        # manage partners
        vals_partner = {
            'name': record.name,
            'fiscalcode': record.fiscalcode,
            self.partner_type: True
        }

        if self.is_fiscalcode(record.fiscalcode):
            vals_partner['fiscalcode'] = record.fiscalcode
        else:
            error = u"Riga {0}: Fiscalcode {1} is not valid".format(self.processed_lines, record.fiscalcode)
            _logger.debug(error)
            self.error.append(error)
            vals_partner['fiscalcode'] = ''

        if self.PARTNER_UNIQUE_OFFICE_CODE:
            if hasattr(record, 'fiscalcode') and record.fiscalcode:
                if len(vals_partner['fiscalcode']) == 6:
                    vals_partner['unique_office_code'] = vals_partner['fiscalcode']

                    if hasattr(record, 'additiona_id') and record.additional_id:
                        vals_partner['fiscalcode'] = vals_partner['additional_id']
                    else:
                        vals_partner['fiscalcode'] = False
            else:
                vals_partner['fiscalcode'] = False

        if self.FORMAT == 'FormatOmnitron':
            if 'customer' in vals_partner:
                del vals_partner['customer']

            if record.client_supplier == u'1':
                vals_partner.update({
                    'supplier': True,
                })
            else:
                vals_partner.update({
                    'customer': True
                })
        else:
            # TODO: Check this code!!!
            if 'supplier' in vals_partner:
                vals_partner.update({
                    'customer': False,
                    'supplier': True
                })

        if hasattr(record, 'person_name') and record.person_name:
            vals_partner['name'] += ' {0}'.format(record.person_name)

        if hasattr(record, 'country_code'):
            country_id = self._country_by_code(cr, uid, record.country_code)
        elif getattr(record, 'country_name'):
            country_id = self._country_by_code(cr, uid, record.country_name)
            if not country_id:
                _logger.error("Can't find country {}".format(record.country_name))
        else:
            country_id = False

        if country_id:
            country = self.pool['res.country'].browse(cr, uid, country_id, self.context)
            country_code = country.code
        else:
            if hasattr(record, 'vat') and record.vat and record.vat[:2] in VAT_CODES:
                country_code = record.vat[:2]
                country_id = self._country_by_code(cr, uid, country_code)
                country = self.pool['res.country'].browse(cr, uid, country_id, self.context)
            else:
                country_code = ''

        if country_id:
            fiscal_position_ids = self.account_fiscal_position_obj.search(
                cr, uid, [('name', '=ilike', country.name)], context=self.context
            )
            if fiscal_position_ids and len(fiscal_position_ids) == 1:
                vals_partner['property_account_position'] = fiscal_position_ids[0]
            else:
                warning = u"Riga {0}: Fiscal position can't be determined for partner {1}".format(
                    self.processed_lines, vals_partner['name'])
                _logger.debug(warning)
                self.warning.append(warning)
        else:
            error = u"Riga {0}: {1} Country non è riconosciuto".format(
                self.processed_lines, vals_partner['name'])
            _logger.debug(error)
            self.error.append(error)

        if hasattr(record, 'fiscal_position') and record.fiscal_position:
            fiscal_position = self.partner_template.map_account_fiscal_position(
                cr, uid, self.partner_template_id, record.fiscal_position)
            if fiscal_position:
                vals_partner['property_account_position'] = fiscal_position

        if hasattr(record, 'payment_term') and record.payment_term:
            vals_payment = self.partner_template.map_payment_term(
                cr, uid, self.partner_template_id, record.payment_term)
            if vals_payment.get('property_payment_term', False):
                vals_partner['property_payment_term'] = vals_payment['property_payment_term']
            if vals_payment.get('company_bank_id', False):
                vals_partner['company_bank_id'] = vals_payment['company_bank_id']

        if hasattr(record, 'credit_limit') and record.credit_limit:
            vals_partner['credit_limit'] = record.credit_limit

        if record.vat and len(record.vat) > 3:
            vals_partner['vat_subjected'] = True
            vals_partner['individual'] = False

            vat = record.vat
            if vat and len(vat) == 10 and country_code[:2] == 'IT':
                vat = '0' + vat
            if vat and len(vat) == 9 and country_code[:2] == 'IT':
                vat = '00' + vat

            if not country_code == record.vat[:2]:
                vals_partner['vat'] = country_code + vat
            else:
                vals_partner['vat'] = vat

            vals_partner['vat'] = vals_partner['vat'].replace(' ', '')
            # if not self.partner_obj.simple_vat_check(cr, uid, country_code.lower(), vals_partner['vat'][2:], None):
            if vatnumber.check_vat(vals_partner['vat']) or vatnumber.check_vat('IT' + vals_partner['vat']):
                if vatnumber.check_vat('IT' + vals_partner['vat']):
                    vals_partner['vat'] = 'IT' + vals_partner['vat']
                if record.vat == record.fiscalcode:
                    if codicefiscale.isvalid(record.vat):
                        vals_partner['fiscalcode'] = vals_partner['vat']
                    else:
                        vals_partner['fiscalcode'] = False
            else:
                error = u"Riga {line}: Partner '{record.code} {record.name}'; Partita IVA errata: <strong>'{vat}'</strong>".format(
                    line=self.processed_lines, record=record, vat=vals_partner['vat']
                )
                _logger.debug(error)
                self.error.append(error)
                if DONT_STOP_ON_WRONG_VAT:
                    del vals_partner['vat']
                    if vals_partner.get('fiscalcode'):
                        del vals_partner['fiscalcode']
                else:
                    return False

        # if record.fiscalcode and not record.fiscalcode == record.vat and not len(record.fiscalcode) == 16:
        #    error = u"Riga {0}: Codice Fiscale {1} errato".format(self.processed_lines, record.fiscalcode)
        #    _logger.debug(error)
        #    self.error.append(error)
        #    return False
        # elif record.fiscalcode and not record.vat:
        #    vals_partner['individual'] = True

        if vals_partner.get('fiscalcode') and not vals_partner.get('vat'):
            vals_partner['individual'] = True

        # if country_code == 'IT':
        #    vals_partner['property_account_position'] = self.italy_fiscal_position_id
        #    if record.vat:
        #        pdb.set_trace()
        #        old_vat = vals_input['Partita IVA']
        #        if len(vals_input['Partita IVA']) < 11:
        #            zero_add = 11 - len(vals_input['Partita IVA'])
        #            for zero in range(0, zero_add):
        #                vals_input['Partita IVA'] = '0' + vals_input['Partita IVA']

        if hasattr(record, 'comment') and record.comment:
            vals_partner['comment'] = record.comment

        record_code = self.simple_string(record.code, as_integer=True)

        if self.UPDATE_ON_CODE and PROPERTY_REF_MAP[self.partner_type]:
            code_partner_ids = self.partner_obj.search(cr, uid, [(PROPERTY_REF_MAP[self.partner_type], '=', record_code)], context=self.context)
        else:
            code_partner_ids = False

        if code_partner_ids and not self.UPDATE_ON_CODE:
            code_partner_data = self.partner_obj.browse(cr, uid, code_partner_ids[0], self.context)
            if vals_partner.get('vat', False) and not code_partner_data.vat == vals_partner['vat']:
                error = u"Riga {0}: Partner '{1} {2}'; codice gia utilizzato per partner {3}. La riga viene ignorata.".format(self.processed_lines, record_code, vals_partner['name'], code_partner_data['name'])
                _logger.debug(error)
                self.error.append(error)
                return False
            elif vals_partner.get('fiscalcode', False) and not code_partner_data.fiscalcode == vals_partner['fiscalcode']:
                error = u"Riga {0}: Partner '{1} {2}'; codice gia utilizzato per partner {3}. La riga viene ignorata.".format(self.processed_lines, record_code, vals_partner['name'], code_partner_data['name'])
                _logger.debug(error)
                self.error.append(error)
                return False
        elif code_partner_ids and self.UPDATE_ON_CODE:
            vals_partner[PROPERTY_REF_MAP[self.partner_type]] = record_code
            if PROPERTY_REF_MAP[self.partner_type] not in self.PARTNER_SEARCH:
                self.PARTNER_SEARCH.insert(0, PROPERTY_REF_MAP[self.partner_type])
        else:
            if record_code:
                vals_partner[PROPERTY_REF_MAP[self.partner_type]] = record_code

        if hasattr(record, 'category') and record.category:
            category_ids = self.category_obj.search(cr, uid, [('name', '=', record.category)], context=self.context)

            if len(category_ids):
                vals_partner['category_id'] = [(6, 0, category_ids)]
            else:
                category_id = self.category_obj.create(cr, uid, {
                    'name': record.category,
                    'active': True
                }, self.context)
                vals_partner['category_id'] = [(6, 0, [category_id])]

        return vals_partner, country_id

    def import_row(self, cr, uid, row_list, book_datemode):
        if not len(row_list) == len(self.HEADER):
            row_str_list = [self.toStr(value) for value in row_list]
            if DEBUG:
                if len(row_list) > len(self.HEADER):
                    pprint(zip(self.HEADER, row_str_list[:len(self.HEADER)]))
                else:
                    pprint(zip(self.HEADER[:len(row_list)], row_str_list))

            error = u"""Row {row}: Row_list is {row_len} long. We expect it to be {expected} long, with this columns:
                            {keys}
                            Instead of this we got this:
                            {header}
                            """.format(row=self.processed_lines, row_len=len(row_list), expected=len(self.HEADER),
                                       keys=self.HEADER, header=', '.join(map(lambda s: s or '', row_str_list)))

            _logger.error(str(row_list))
            _logger.error(error)
            # error = u'Riga {0} non importata. Colonne non corrsipondono al Header definito'.format(self.processed_lines)
            # _logger.debug(error)
            # self.error.append(error)
            return False

        if DEBUG:
            # pprint(row_list)
            row_str_list = [self.simple_string(value) for value in row_list]
            pprint(zip(self.HEADER, row_str_list))

        record = self.Record._make([self.toStr(value) for value in row_list])

        if self.first_row:
            if not record.name:
                warning = u'Riga {0}: Trovato Header'.format(self.processed_lines)
                _logger.debug(warning)
                self.warning.append(warning)
                return True
            else:
                for column in record:
                    # column_ascii = unicodedata.normalize('NFKD', column).encode('ascii', 'ignore').lower()
                    if column in self.HEADER:
                        warning = u'Riga {0}: Trovato Header'.format(self.processed_lines)
                        _logger.debug(warning)
                        self.warning.append(warning)
                        return True

        collected_values = self.collect_values(cr, uid, record)
        if collected_values:
            vals_partner, country_id = collected_values
        else:
            return False

        record_code = self.simple_string(record.code, as_integer=True)

        partner_id = self._find_partner(cr, uid, vals_partner)

        if partner_id and partner_id > 0:
            self.partner_obj.write(cr, uid, partner_id, vals_partner, self.context)
            self.updated += 1
        elif partner_id and partner_id < 0:
            return False
        else:
            self.context['import'] = True
            try:
                partner_id = self.partner_obj.create(cr, uid, vals_partner, self.context)
                self.uo_new += 1
            # except ValidateError as e:
            except IntegrityError as e:
                error = u"Riga {0}: Partner '{1} {2}'. I dati non corretti. (Error: {3}) La riga viene ignorata.".format(
                    self.processed_lines, record_code, vals_partner['name'], e)
                _logger.debug(error)
                self.error.append(error)
                return False
            except Exception as e:
                # e = sys.exc_info()[0]
                e = e[1].split(':')

                if len(e) > 1:
                    e = e[1]
                error = u"Riga {0}: Partner '{1} {2}'. I dati non corretti. (Error: {3}) La riga viene ignorata.".format(
                    self.processed_lines, record_code, vals_partner['name'], e)
                _logger.debug(error)
                self.error.append(error)
                return False

        address_type_1 = self.ADDRESS_TYPE[0]
        address_type_2 = self.ADDRESS_TYPE[1]

        if getattr(record, 'street_' + address_type_1) or getattr(record, 'zip_' + address_type_1) or getattr(record, 'city_' + address_type_1) or getattr(record, 'province_' + address_type_1):
            first_address = True
        else:
            first_address = False

        if getattr(record, 'street_' + address_type_2) or getattr(record, 'zip_' + address_type_2) or getattr(record, 'city_' + address_type_2) or getattr(record, 'province_' + address_type_2):
            second_address = True
        else:
            second_address = False

        if first_address and second_address:
            self.write_address(cr, uid, address_type_1, partner_id, record, vals_partner, country_id)
            self.write_address(cr, uid, address_type_2, partner_id, record, vals_partner, country_id)
        elif first_address:
            self.write_address(cr, uid, address_type_1, partner_id, record, vals_partner, country_id, force_default=True)
        elif second_address:
            self.write_address(cr, uid, address_type_2, partner_id, record, vals_partner, country_id, force_default=True)

        if self.FORMAT == 'FormatOmnitron':
            if hasattr(record, 'email_invoice') and record.email_invoice:
                self.write_address(cr, uid, 'invoice', partner_id, record, vals_partner, country_id)

        if hasattr(record, 'iban') and record.iban:
            self.get_or_create_bank(cr, uid, record.iban, partner_id, self.context)

        return partner_id
