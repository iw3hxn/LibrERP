# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2014 Didotech srl (info at didotech.com)
#
#                          All Rights Reserved.
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler
import threading
from tools.translate import _
import math
import data_migration.settings as settings
from collections import namedtuple
from pprint import pprint
from utils import Utils
from osv import osv

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

import xlrd

COUNTRY_CODES = settings.COUNTRY_CODES
DEBUG = settings.DEBUG

if DEBUG:
    import pdb

PROPERTY_REF_MAP = {
    'supplier': 'property_supplier_ref',
    'customer': 'property_customer_ref'
}

UPDATE_ON_CODE = True
DONT_STOP_ON_WRONG_VAT = True


class ImportFile(threading.Thread, Utils):
    def __init__(self, cr, uid, ids, context):
        # Inizializzazione superclasse
        threading.Thread.__init__(self)

        # Inizializzazione classe ImportPartner
        self.uid = uid
        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        self.partner_obj = self.pool['res.partner']
        self.category_obj = self.pool['res.partner.category']
        self.address_obj = self.pool['res.partner.address']
        self.city_obj = self.pool['res.city']
        self.province_obj = self.pool['res.province']
        self.account_fiscal_position_obj = self.pool['account.fiscal.position']

        # Necessario creare un nuovo cursor per il thread, quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()

        self.partnerImportID = ids[0]

        self.context = context
        self.error = []
        self.warning = []
        self.first_row = True

        # Contatori dei nuovi partner inseriti e aggiornati, vengono utilizzati per compilare il
        # rapporto alla terminazione del processo di import
        self.uo_new = 0
        self.updated = 0
        self.problems = 0

    def run(self):
        # Recupera il record dal database
        self.filedata_obj = self.pool['partner.import']
        self.partnerImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.partnerImportID, context=self.context)
        self.file_name = self.partnerImportRecord.file_name.split('\\')[-1]
        self.strict = self.partnerImportRecord.strict

        #===================================================
        Config = getattr(settings, self.partnerImportRecord.format)

        self.HEADER = Config.HEADER_CUSTOMER
        self.REQUIRED = Config.REQUIRED
        self.PARTNER_SEARCH = Config.PARTNER_SEARCH
        self.ADDRESS_TYPE = Config.ADDRESS_TYPE

        if not len(self.HEADER) == len(Config.COLUMNS.split(',')):
            pprint(zip(self.HEADER, Config.COLUMNS.split(',')))
            raise osv.except_osv('Error: wrong configuration!', 'The length of columns and headers must be the same')

        self.Record = namedtuple('Record', Config.COLUMNS)
        #===================================================

        self.partner_type = self.partnerImportRecord.partner_type

        for encoding in ('utf-8', 'latin-1', 'cp1252'):
            try:
                book = xlrd.open_workbook(file_contents=self.partnerImportRecord.content_text, encoding_override=encoding)
                break
            except:
                pass
        else:
            raise osv.except_osv('Error', _('Unknown encoding'))

        sheet = []
        sh = book.sheet_by_index(0)

        for rx in range(sh.nrows):
            row = []
            for cx in range(sh.ncols):
                row.append(sh.cell_value(rowx=rx, colx=cx))
            sheet.append(row)

        self.numberOfLines = sh.nrows

        if DEBUG:
            # Importa i partner
            self.process(self.cr, self.uid, sheet, book.datemode)

            # Genera il report sull'importazione
            self.notify_import_result(self.cr, self.uid, 'Importazione partner')
        else:
            # Elaborazione del Partner
            try:
                # Import partner
                self.process(self.cr, self.uid, sheet, book.datemode)

                # Genera il report sull'importazione
                self.notify_import_result(self.cr, self.uid, 'Importazione partner')
            except Exception as e:
                # Annulla le modifiche fatte
                self.cr.rollback()
                self.cr.commit()

                title = "Import failed"
                message = u"Errore alla linea %s" % self.processed_lines + "\nDettaglio:\n\n" + str(e)

                if DEBUG:
                    ### Debug
                    print message
                    pdb.set_trace()
                self.notify_import_result(self.cr, self.uid, title, message, error=True)

    def process(self, cr, uid, table, book_datemode):
        self.progressIndicator = 0

        notifyProgressStep = (self.numberOfLines / 100) + 1

        for self.processed_lines, row_list in enumerate(table, start=1):
            # Import row
            if not self.import_row(cr, uid, row_list, book_datemode):
                self.problems += 1

            if (self.processed_lines % notifyProgressStep) == 0:
                cr.commit()
                completedQuota = float(self.processed_lines) / float(self.numberOfLines)
                completedPercentage = math.trunc(completedQuota * 100)
                self.progressIndicator = completedPercentage
                self.updateProgressIndicator(cr, uid, self.partnerImportID)

        self.progressIndicator = 100
        self.updateProgressIndicator(cr, uid, self.partnerImportID)

        return True

    #def _find_partner(self, cr, uid, record):
    #    for field in self.PARTNER_SEARCH:
    #        if getattr(record, field):
    #            _logger.info(u"{0} = {1}".format(field, getattr(record, field)))
    #            partner_ids = self.partner_obj.search(cr, uid, [(field, '=', getattr(record, field))])
    #            if len(partner_ids) == 1:
    #                return partner_ids[0]
    #            elif len(partner_ids) > 1:
    #                error = u'Riga {line}: Trovati più clienti con {field} = {name}'.format(line=self.processed_lines, field=field, name=getattr(record, field))
    #                _logger.debug(error)
    #                self.error.appen(error)
    #                return False
    #    return False

    def _find_partner(self, cr, uid, vals_partner, context=None):
        partner_clone = set()
        for field in self.PARTNER_SEARCH:
            if vals_partner.get(field, False):
                _logger.info(u"{0} = {1}".format(field, vals_partner[field]))
                partner_ids = self.partner_obj.search(cr, uid, [(field, '=', vals_partner[field])])
                if len(partner_ids) == 1:
                    if self.strict:
                        partner_clone.add(partner_ids[0])
                    else:
                        return partner_ids[0]
                elif len(partner_ids) > 1:
                    error = u'Riga {line}: Trovati più clienti con {field} = {name}'.format(line=self.processed_lines, field=field, name=vals_partner[field])
                    _logger.debug(error)
                    self.error.append(error)
                    return -1
        
        if len(partner_clone) == 1:
            partner_id = partner_clone.pop()
            partner = self.partner_obj.browse(cr, uid, partner_id, context)
            for field in self.PARTNER_SEARCH:
                if vals_partner.get(field, False) and not vals_partner[field] == getattr(partner, field):
                    error = u'Riga {line}: Trovati più cloni del cliente {name}'.format(line=self.processed_lines, name=partner.name)
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

    def _contry_by_code(self, cr, uid, code):
        country_ids = self.pool['res.country'].search(cr, uid, [('code', '=', code)])
        if country_ids:
            return country_ids[0]
        else:
            return False

    def write_address(self, cr, uid, address_type, partner_id, record, vals_partner, country_code, force_default=False):
        vals_address = {
            'partner_id': partner_id,
            'name': vals_partner['name'],
            'type': address_type,
            'active': True,
        }

        if force_default:
            vals_address['type'] = 'default'

        for field in ('street', 'street2', 'city', 'zip', 'email', 'phone', 'fax'):
            if hasattr(record, field + '_' + address_type) and getattr(record, field + '_' + address_type):
                vals_address[field] = getattr(record, field + '_' + address_type)

        if len(record.fiscalcode) == 16 and not record.person_name:
            vals_address['name'] = ''

        if not hasattr(record, 'zip' + '_' + address_type) and 'city' in vals_address:
            city_ids = self.city_obj.search(cr, uid, [('name', '=', vals_address['city'])])
            if city_ids:
                city_data = self.city_obj.browse(cr, uid, city_ids[0])
                vals_address['zip'] = city_data.zip

        if hasattr(record, 'province ' + address_type):
            province_ids = self.province_obj.search(cr, uid, [('code', '=', getattr(record, 'province ' + address_type))])
            if province_ids:
                vals_address['province'] = province_ids[0]
                province_data = self.province_obj.browse(cr, uid, province_ids[0])
                vals_address['region'] = province_data.region.id

        if record.country_code:
            vals_address['country_id'] = self._contry_by_code(cr, uid, country_code)

            address_ids = self.address_obj.search(cr, uid, [('partner_id', '=', vals_address['partner_id']), ('type', '=', vals_address['type'])])
            if address_ids:
                address_id = address_ids[0]
                self.address_obj.write(cr, uid, address_id, vals_address)
            else:
                address_id = self.address_obj.create(cr, uid, vals_address)

        return True

    def import_row(self, cr, uid, row_list, book_datemode):
        if not len(row_list) == len(self.HEADER):
            error = u'Riga {0} non importata. Colonne non corrsipondono al Header definito'.format(self.processed_lines)
            _logger.debug(error)
            self.error.append(error)
            return False

        record = self.Record._make([self.toStr(value) for value in row_list])

        if self.first_row:
            if not record.name:
                warning = u'Riga {0}: Trovato Header'.format(self.processed_lines)
                _logger.debug(warning)
                self.warning.append(warning)
                return True
            else:
                for column in record:
                    #column_ascii = unicodedata.normalize('NFKD', column).encode('ascii', 'ignore').lower()
                    if column in self.HEADER:
                        warning = u'Riga {0}: Trovato Header'.format(self.processed_lines)
                        _logger.debug(warning)
                        self.warning.append(warning)
                        return True

        self.first_row = False

        for field in self.REQUIRED:
            if not getattr(record, field):
                error = u"Riga {0}: Manca il valore della {1}. La riga viene ignorata.".format(self.processed_lines, field)
                _logger.debug(error)
                self.error.append(error)
                return False

        # manage partners
        vals_partner = {
            'name': record.name,
            'fiscalcode': record.fiscalcode,
            self.partner_type: True
        }

        if hasattr(record, 'person_name') and record.person_name:
            vals_partner['name'] += ' {0}'.format(record.person_name)

        country_code = COUNTRY_CODES.get(record.country_code, record.country_code)

        if country_code:
            country_id = self._contry_by_code(cr, uid, country_code)
            if country_id:
                country = self.pool['res.country'].browse(cr, uid, country_id)
                fiscal_position_ids = self.account_fiscal_position_obj.search(cr, uid, [('name', '=ilike', country.name)])
                if fiscal_position_ids and len(fiscal_position_ids) == 1:
                    vals_partner['property_account_position'] = fiscal_position_ids[0]
                else:
                    warning = u"Riga {0}: Fiscal position can't be determined for partner {1}".format(self.processed_lines, vals_partner['name'])
                    _logger.debug(warning)
                    self.warning.append(warning)
            else:
                error = u"Riga {0}: Country code '{1}' non è riconosciuto. La riga viene ignorata.".format(self.processed_lines, country_code)
                _logger.debug(error)
                self.error.append(error)
                return False

        if record.vat and len(record.vat) > 3:
            vals_partner['vat_subjected'] = True
            vals_partner['individual'] = False

            if not country_code == record.vat[:2]:
                vals_partner['vat'] = country_code + record.vat
            else:
                vals_partner['vat'] = record.vat

            if not self.partner_obj.simple_vat_check(cr, uid, country_code.lower(), vals_partner['vat'][2:], None):
                error = u"Riga {line}: Partner '{record.code} {record.name}'; Partita IVA errata: {record.vat}".format(line=self.processed_lines, record=record)
                _logger.debug(error)
                self.error.append(error)
                if DONT_STOP_ON_WRONG_VAT:
                    del vals_partner['vat']
                else:
                    return False

            if record.vat == record.fiscalcode:
                vals_partner['fiscalcode'] = vals_partner['vat']

        # if record.fiscalcode and not record.fiscalcode == record.vat and not len(record.fiscalcode) == 16:
        #    error = u"Riga {0}: Codice Fiscale {1} errato".format(self.processed_lines, record.fiscalcode)
        #    _logger.debug(error)
        #    self.error.append(error)
        #    return False
        # elif record.fiscalcode and not record.vat:
        #    vals_partner['individual'] = True

        if record.fiscalcode and not record.vat:
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

        code_partner_ids = self.partner_obj.search(cr, uid, [(PROPERTY_REF_MAP[self.partner_type], '=', record.code)])

        if code_partner_ids and not UPDATE_ON_CODE:
            code_partner_data = self.partner_obj.browse(cr, uid, code_partner_ids[0])
            if vals_partner.get('vat', False) and not code_partner_data.vat == vals_partner['vat']:
                error = u"Riga {0}: Partner '{1} {2}'; codice gia utilizzato per partner {3}. La riga viene ignorata.".format(self.processed_lines, record.code, vals_partner['name'], code_partner_data['name'])
                _logger.debug(error)
                self.error.append(error)
                return False
            elif vals_partner.get('fiscalcode', False) and not code_partner_data.fiscalcode == vals_partner['fiscalcode']:
                error = u"Riga {0}: Partner '{1} {2}'; codice gia utilizzato per partner {3}. La riga viene ignorata.".format(self.processed_lines, record.code, vals_partner['name'], code_partner_data['name'])
                _logger.debug(error)
                self.error.append(error)
                return False
        elif code_partner_ids and UPDATE_ON_CODE:
            vals_partner[PROPERTY_REF_MAP[self.partner_type]] = record.code
            if PROPERTY_REF_MAP[self.partner_type] not in self.PARTNER_SEARCH:
                self.PARTNER_SEARCH.insert(0, PROPERTY_REF_MAP[self.partner_type])
        else:
            vals_partner[PROPERTY_REF_MAP[self.partner_type]] = record.code

        if hasattr(record, 'category') and record.category:
            category_ids = self.category_obj.search(cr, uid, [('name', 'ilike', record.category)])

            if len(category_ids) == 1:
                vals_partner['category_id'] = [(6, 0, category_ids)]
            else:
                vals_partner['category_id'] = [(6, 0, [self.category_obj.create(cr, uid, {
                    'name': record.category,
                    'active': True
                })])]

        # partner_id = self._find_partner(cr, uid, record)
        partner_id = self._find_partner(cr, uid, vals_partner)

        if partner_id and partner_id > 0:
            self.partner_obj.write(cr, uid, partner_id, vals_partner, self.context)
            self.updated += 1
        elif partner_id and partner_id < 0:
            return False
        else:
            self.context['import'] = True
            partner_id = self.partner_obj.create(cr, uid, vals_partner, self.context)
            self.uo_new += 1

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
            self.write_address(cr, uid, address_type_1, partner_id, record, vals_partner, country_code)
            self.write_address(cr, uid, address_type_2, partner_id, record, vals_partner, country_code)
        elif first_address:
            self.write_address(cr, uid, address_type_1, partner_id, record, vals_partner, country_code, force_default=True)
        elif second_address:
            self.write_address(cr, uid, address_type_2, partner_id, record, vals_partner, country_code, force_default=True)

        return partner_id
