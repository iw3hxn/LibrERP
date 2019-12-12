# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Didotech SRL
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
import xlrd
from openerp.addons.core_extended.file_manipulation import import_sheet
from tools.translate import _

from openerp.addons.data_migration import settings
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from utils import Utils

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

DEBUG = settings.DEBUG

if DEBUG:
    import pdb


class ImportFile(threading.Thread, Utils):
    def __init__(self, cr, uid, ids, context):
        # Inizializzazione superclasse
        threading.Thread.__init__(self)
        
        # Inizializzazione classe ImportPricelist
        self.uid = uid
        self.start_time = datetime.now()
        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        self.product_obj = self.pool['product.product']
        self.picking_obj = self.pool['stock.picking']
        self.move_obj = self.pool['stock.move']
        self.location_obj = self.pool['stock.location']

        # Necessario creare un nuovo cursor per il thread,
        # quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile
        # all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()
        
        self.pickingImportID = ids[0]
        
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
        self.cache = {}
        self.cache_product = {}
        self.cache_uom_product = {}
    
    def run(self):
        try:
            # Recupera il record dal database
            self.filedata_obj = self.pool['picking.import']
            self.pickingImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.pickingImportID, context=self.context)
            self.file_name = self.pickingImportRecord.file_name.split('\\')[-1]
            self.address_id = self.pickingImportRecord.address_id
            self.stock_journal_id = self.pickingImportRecord.stock_journal_id
            self.location_id = self.pickingImportRecord.location_id
            self.location_dest_id = self.pickingImportRecord.location_dest_id

            # ===================================================
            Config = getattr(settings, self.pickingImportRecord.format)

            self.HEADER = Config.HEADER_PICKING
            self.REQUIRED = Config.REQUIRED_PICKING

            if not len(self.HEADER) == len(Config.COLUMNS_PICKING.split(',')):
                pprint(zip(self.HEADER, Config.COLUMNS_PICKING.split(',')))
                raise orm.except_orm('Error: wrong configuration!', 'The length of columns and headers must be the same')

            self.RecordPicking = namedtuple('RecordPicking', Config.COLUMNS_PICKING)

            # ===================================================

            table, self.numberOfLines = import_sheet(self.file_name, self.pickingImportRecord.content_text)
        except Exception as e:
                # Annulla le modifiche fatte
                self.cr.rollback()
                self.cr.commit()

                title = "Import failed"
                message = "Errore nell'importazione del file %s" % self.file_name + "\nDettaglio:\n\n" + str(e)

                if DEBUG:
                    ### Debug
                    _logger.debug(message)
                    pdb.set_trace()
                self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.pickingImportRecord)

        if DEBUG:
            # Importa il file
            self.process(self.cr, self.uid, table)
            
            # Genera il report sull'importazione
            self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.pickingImportRecord)
        else:
            # Elaborazione del file
            try:
                # Importa il listino
                self.process(self.cr, self.uid, table)
                
                # Genera il report sull'importazione
                self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.pickingImportRecord)
            except Exception as e:
                # Annulla le modifiche fatte
                self.cr.rollback()
                self.cr.commit()
                
                title = "Import failed"
                message = "Errore alla linea %s" % str(self.processed_lines) + "\nDettaglio:\n\n" + str(e)
                
                if DEBUG:
                    ### Debug
                    _logger.debug(message)
                    pdb.set_trace()
                
                self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.pickingImportRecord)

    def process(self, cr, uid, table):
        self.message_title = _("Importazione Picking")
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
                self.updateProgressIndicator(cr, uid, self.pickingImportID)

        # here is import all now need to

        for pick in self.cache:
            picking = self.picking_obj.browse(cr, uid, [self.cache[pick]], context=self.context)[0]
            try:
                self.picking_obj.draft_validate(cr, uid, [self.cache[pick]], context=self.context)
                move_ids = self.move_obj.search(cr, uid, [('picking_id', 'in', [self.cache[pick]])], context=self.context)
                self.move_obj.write(cr, uid, move_ids, {'date': picking.date_done}, context=self.context)
            except Exception as e:
                title = "Import failed"
                message = "Errore nel picking %s" % pick + "\nDettaglio:\n\n" + str(e)
                _logger.error(message)
                self.error.append(message)

        self.progressIndicator = 100
        self.updateProgressIndicator(cr, uid, self.pickingImportID)
        
        return True
    
    def import_row(self, cr, uid, row_list):

        if self.first_row:
            row_str_list = [self.toStr(value) for value in row_list]
            for column in row_str_list:
                # print column
                if column in self.HEADER:
                    _logger.info('Riga {0}: Trovato Header'.format(self.processed_lines))
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
                """.format(row=self.processed_lines, row_len=len(row_list), expected=len(self.HEADER), keys=self.HEADER, header=', '.join(row_str_list))

            _logger.error(str(row_list))
            _logger.error(error)
            self.error.append(error)
            return False
        elif DEBUG:
            # pprint(row_list)
            row_str_list = [self.simple_string(value) for value in row_list]
            pprint(zip(self.HEADER, row_str_list))

        # Sometime value is only numeric and we don't want string to be treated as Float
        record = self.RecordPicking._make([self.simple_string(value) for value in row_list])
        for field in self.REQUIRED:
            if not getattr(record, field):
                error = "Riga {0}: Manca il valore della {1}. La riga viene ignorata.".format(self.processed_lines, field)
                _logger.debug(error)
                self.error.append(error)
                return False

        # date = datetime.datetime(*xlrd.xldate_as_tuple(float(record.date), 0)).strftime("%d/%m/%Y %H:%M:%S")
        if record.date.replace('.', '').isdigit():
            # Ex: u'42359.0' -> '2015-12-21 00:00:00'
            date = datetime(*xlrd.xldate_as_tuple(float(record.date), 0)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            date = record.date[:19]

        origin = record.origin.split('.')[0]
        picking_type = self.location_obj.picking_type_get(cr, uid, self.location_id, self.location_dest_id)

        if self.cache.get(origin):
            picking_id = self.cache[origin]
            _logger.info(u'Picking {0} already processed in cache'.format(origin))
            #    picking_id = picking_id[0]
        elif self.picking_obj.search(cr, uid, [('origin', '=', origin), ('state', '=', 'draft'), ('type', '=', picking_type)], context=self.context):
            picking_id = self.picking_obj.search(cr, uid, [('origin', '=', origin), ('state', '=', 'draft'), ('type', '=', picking_type)], context=self.context)[0]
            self.cache[origin] = picking_id
            _logger.warning(u'Picking {0} already exist'.format(origin))
        else:
            # i need to create stock.picking
            # so need to create one
            # picking_type = self.location_obj.picking_type_get(cr, uid, self.location_id, self.location_dest_id)
            invoice_state = self.stock_journal_id and self.stock_journal_id.default_invoice_state or 'none'
            vals_picking = {
                'address_id': self.address_id.id,
                'origin': origin,
                'type': picking_type,
                'move_type': 'one',
                'invoice_state': invoice_state,
                'auto_picking': True,
                'stock_journal_id': self.stock_journal_id.id,
                'min_date': date,
                'date': date,
            }
            picking_id = self.picking_obj.create(cr, uid, vals_picking, context=self.context)
            self.cache[origin] = picking_id
            _logger.info(u'Create Picking {0} '.format(origin))
        
        vals_move = {}
        product_id = False
        if hasattr(record, 'product') and record.product:
            product = record.product
            if self.cache_product.get(product):
                product_id = self.cache_product[product]
                _logger.warning(u'Product {0} already processed in cache'.format(product))
            else:
                product_ids = self.product_obj.search(cr, uid, [('default_code', '=', product)], context=self.context)
                if not product_ids:
                    product_ids = self.product_obj.search(cr, uid, [('default_code', 'ilike', product)], context=self.context)
                    if not product_ids:
                        product_ids = self.product_obj.search(cr, uid, [('name', '=', product)], context=self.context)
                        if not product_ids:
                            product_ids = self.product_obj.search(cr, uid, [('name', 'ilike', product)], context=self.context)
                            if not product_ids:
                                product_ids = self.product_obj.search(cr, uid, [('ean13', '=', product)], context=self.context)
                if product_ids:
                    product_id = product_ids[0]
                    self.cache_product[product] = product_id
                    self.cache_uom_product[product_id] = self.product_obj.browse(cr, uid, product_id, self.context).uom_id.id
                else:
                    error = u'Row {row}: Product "{product}" not Found'.format(row=self.processed_lines, product=product)
                    _logger.error(error)
                    self.error.append(error)

        if hasattr(record, 'qty') and record.qty:
            vals_move['product_qty'] = float(record.qty)

        if product_id:
            vals_move.update({
                'name': origin,
                'picking_id': picking_id,
                'product_id': product_id,
                'product_uom': self.cache_uom_product[product_id],
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'date': date,
                'date_expected': date,
            })

            _logger.info(u'Row {row}: Adding product {product} to picking {picking}'.format(row=self.processed_lines, product=record.product, picking=origin))

            self.move_obj.create(cr, uid, vals_move, self.context)
            self.uo_new += 1
        else:
            _logger.warning(u'Row {row}: Not Find {product}'.format(row=self.processed_lines, product=record.product))

        return product_id
