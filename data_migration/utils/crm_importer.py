# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016-2019 Didotech SRL (info at didotech.com)
#
#                          All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import logging
import math
import threading
from collections import namedtuple
from datetime import datetime
from pprint import pprint

import pooler
from openerp.addons.core_extended.file_manipulation import import_sheet
from openerp.addons.data_migration import settings
from openerp.osv import orm
from tools.translate import _

from utils import Utils

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

COUNTRY_CODES = settings.COUNTRY_CODES
DEBUG = settings.DEBUG

# if DEBUG:
#     import pdb


class ImportFile(threading.Thread, Utils):
    def __init__(self, cr, uid, ids, context):
        # Inizializzazione superclasse
        threading.Thread.__init__(self)
        
        # Inizializzazione classe ImportPricelist
        self.uid = uid
        self.start_time = datetime.now()
        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        self.crm_lead_obj = self.pool['crm.lead']
        
        # Necessario creare un nuovo cursor per il thread,
        # quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile
        # all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()
        self.city_obj = self.pool['res.city']
        self.province_obj = self.pool['res.province']
        self.state_obj = self.pool['res.country.state']
        self.categoty_obj = self.pool['res.partner.category']
        
        self.crmImportID = ids[0]
        
        self.context = context
        self.error = []
        self.warning = []
        self.first_row = True
        
        # Contatori dei nuovi prodotti inseriti e dei prodotti aggiornati,
        # vengono utilizzati per compilare il rapporto alla terminazione
        # del processo di import
        self.uo_new = 0
        self.updated = 0
        self.problems = 0
        self.cache = []
    
    def run(self):
        # Recupera il record dal database
        self.filedata_obj = self.pool['crm.import']
        self.CrmImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.crmImportID, context=self.context)
        self.file_name = self.CrmImportRecord.file_name.split('\\')[-1]
        self.shop_id = self.CrmImportRecord.shop_id

        # ===================================================
        Config = getattr(settings, self.CrmImportRecord.format)

        self.HEADER = Config.HEADER_CRM
        self.REQUIRED = Config.REQUIRED_CRM
        self.COLUMNS_CRM = Config.COLUMNS_CRM
        self.CRM_SEARCH = Config.CRM_SEARCH
        self.CRM_WARNINGS = Config.CRM_WARNINGS
        self.CRM_ERRORS = Config.CRM_ERRORS
        self.FORMAT = self.CrmImportRecord.format

        # Default values
        self.CRM_DEFAULTS = Config.CRM_DEFAULTS
        
        if not len(self.HEADER) == len(Config.COLUMNS_CRM):
            pprint(zip(self.HEADER, Config.COLUMNS_CRM))
            raise orm.except_orm('Error: wrong configuration!', 'The length of columns and headers must be the same')
        
        self.RecordCrm = namedtuple('RecordProduct', Config.COLUMNS_CRM)

        # ===================================================
        try:
            table, self.numberOfLines = import_sheet(self.file_name, self.CrmImportRecord.content_text)
        except Exception as e:
            # Annulla le modifiche fatte
            self.cr.rollback()
            self.cr.commit()

            title = "Import failed"
            message = "Errore nell'importazione del file %s" % self.file_name + "\nDettaglio:\n\n" + str(e)

            if DEBUG:
                ### Debug
                _logger.debug(message)
                # pdb.set_trace()
            self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.CrmImportRecord)

        if DEBUG:
            # Importa il listino
            try:
                self.process(self.cr, self.uid, table)
            
                # Genera il report sull'importazione

                self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.CrmImportRecord)
            except Exception as e:
                title = "Import failed"
                message = "Errore alla linea %s" % self.processed_lines + "\nDettaglio:\n\n" + str(e)

        else:
            # Elaborazione del listino prezzi
            try:
                # Importa il listino
                self.process(self.cr, self.uid, table)
                
                # Genera il report sull'importazione
                self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.CrmImportRecord)
            except Exception as e:
                # Annulla le modifiche fatte
                self.cr.rollback()
                self.cr.commit()
                
                title = "Import failed"
                message = "Errore alla linea %s" % self.processed_lines + "\nDettaglio:\n\n" + str(e)
                
                if DEBUG:
                    ### Debug
                    _logger.debug(message)
                    # pdb.set_trace()
                
                self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.CrmImportRecord)

    def process(self, cr, uid, table):
        self.message_title = _("Importazione CRM")
        self.progressIndicator = 0
        
        notifyProgressStep = (self.numberOfLines / 100) + 1     # NB: divisione tra interi da sempre un numero intero!
                                                                # NB: il + 1 alla fine serve ad evitare divisioni per zero
        
        # Use counter of processed lines
        # If this line generate an error we will know the right Line Number
        for self.processed_lines, row_list in enumerate(table, start=1):

            if not self.import_row(cr, uid, row_list):
                self.problems += 1
                
            if (self.processed_lines % notifyProgressStep) == 0:
                cr.commit()
                completedQuota = float(self.processed_lines) / float(self.numberOfLines)
                completedPercentage = math.trunc(completedQuota * 100)
                self.progressIndicator = completedPercentage
                self.updateProgressIndicator(cr, uid, self.crmImportID)
        
        self.progressIndicator = 100
        self.updategressIndProicator(cr, uid, self.crmImportID)
        
        return True

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

    def import_row(self, cr, uid, row_list):

        if self.first_row:
            row_str_list = [self.simple_string(value) for value in row_list]
            for column in row_str_list:
                # print column
                if column in self.HEADER:
                    _logger.info('Riga {0}: Trovato Header'.format(self.processed_lines))
                    self.first_row = True
                    return True
            self.first_row = False
        if not len(row_list) == len(self.HEADER):
            row_str_list = [self.simple_string(value) for value in row_list]
            if DEBUG:
                if len(row_list) > len(self.HEADER):
                    pprint(zip(self.HEADER, row_str_list[:len(self.HEADER)]))
                else:
                    pprint(zip(self.HEADER[:len(row_list)], row_str_list))

            error = u"""Row {row}: Row_list is {row_len} long. We expect it to be {expected} long, with this columns:
                {keys}
                Instead of this we got this:
                {header}
                """.format(row=self.processed_lines, row_len=len(row_list), expected=len(self.HEADER), keys=self.HEADER, header=', '.join(map(lambda s: s or '', row_str_list)))

            _logger.error(str(row_list))
            _logger.error(error)
            self.error.append(error)
            return False
        elif DEBUG:
            # pprint(row_list)
            row_str_list = [self.simple_string(value) for value in row_list]
            pprint(zip(self.HEADER, row_str_list))
        
        # Sometime value is only numeric and we don't want string to be treated as Float
        record = self.RecordCrm._make([self.simple_string(value) for value in row_list])
        # import pdb; pdb.set_trace()
        if record.partner_name and record.partner_name in self.cache:
            _logger.warning(u'Partner {0} already processed'.format(record.partner_name))
            # return False
        elif record.partner_name:
            self.cache.append(record.partner_name)
        
        for field in self.REQUIRED:
            if not getattr(record, field):
                error = "Riga {0}: Manca il valore della {1}. La riga viene ignorata.".format(self.processed_lines, field)
                _logger.debug(error)
                self.error.append(error)
                return False

        # print '>>>>>>>', record.name
        vals_crm = self.crm_lead_obj.default_get(cr, uid, [], self.context)

        for field in self.CRM_SEARCH:
            if hasattr(record, field) and getattr(record, field):
                vals_crm[field] = getattr(record, field)
                break
        else:
            error = "Row {0}: Can't find valid crm key".format(self.processed_lines)
            _logger.error(error)
            self.error.append(error)
            return False

        vals_crm['vat'] = ''  # Null value
        for field in self.COLUMNS_CRM:
            if hasattr(record, field) and getattr(record, field):
                vals_crm[field] = getattr(record, field)

        if self.FORMAT == 'FormatOne':
            if len(vals_crm['vat']) == 11:
                vat_country = 'IT'
                vat_number = vals_crm['vat']
                vals_crm['vat'] = (vat_country + vat_number).upper()

            vals_crm['shop_id'] = self.shop_id and self.shop_id.id

            crm_ids = self.crm_lead_obj.search(cr, uid, [(field, '=ilike', vals_crm['partner_name'].replace('\\', '\\\\'))], context=self.context)
        else:
            if record.zip:
                vals_crm['zip'] = self.simple_string(record.zip, as_integer=True)

                # vals_crm['zip'] = vals_crm.get('zip') and vals_crm['zip'].isdigit() and self.simple_string(record.zip, as_integer=False) or ''
                vals_crm.update(self.crm_lead_obj.on_change_zip(cr, uid, [], vals_crm['zip']).get('value'))

            if vals_crm.get('country_id'):
                if not isinstance(vals_crm['country_id'], int):
                    vals_crm['country_id'] = self._country_by_code(cr, uid, vals_crm['country_id'])

            if vals_crm.get('partner_category_id'):
                if not isinstance(vals_crm['partner_category_id'], int):
                    partner_category_ids = self.categoty_obj.search(cr, uid, [('name', '=', vals_crm['partner_category_id'])])
                    vals_crm['partner_category_id'] = partner_category_ids and partner_category_ids[0]
            search_domain = []
            crm_ids = []
            if vals_crm.get('partner_name', False):
                search_domain.append(('partner_name', '=', vals_crm['partner_name'].replace('\\', '\\\\')))
            if vals_crm.get('email_from', False):
                search_domain.append(('email_from', '=', vals_crm['email_from'].replace('\\', '\\\\')))
                crm_ids = self.crm_lead_obj.search(cr, uid, search_domain, context=self.context)
        if crm_ids:
            _logger.info(u'Row {row}: Updating Lead Partner {partner}...'.format(row=self.processed_lines, partner=vals_crm['partner_name']))
            crm_id = crm_ids[0]
            if self.crm_lead_obj.search(cr, uid, [('id', '=', crm_id), ('state', '=', 'draft')]):
                try:
                    self.crm_lead_obj.write(cr, uid, crm_id, vals_crm, self.context)
                except Exception as e:
                    print (e)
            else:
                _logger.error(u'Row {row}: Lead Partner {partner} just exist and not in draft...'.format(row=self.processed_lines,
                                                                                     partner=vals_crm['partner_name']))
            self.updated += 1
        else:
            _logger.info(u'Row {row}: Adding Lead Partner {partner}...'.format(row=self.processed_lines, partner=vals_crm['partner_name']))
            default_vals_crm = self.CRM_DEFAULTS.copy()
            default_vals_crm.update(vals_crm)

            crm_id = self.crm_lead_obj.create(cr, uid, default_vals_crm, self.context)
            self.uo_new += 1

        return crm_id

