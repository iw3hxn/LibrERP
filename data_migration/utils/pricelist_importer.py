# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2016 Didotech SRL (info at didotech.com)
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
from tools.translate import _

from openerp.addons.data_migration import settings
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
        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        self.pricelist_ver_obj = self.pool['product.pricelist.version']
        self.pricelist_item_obj = self.pool['product.pricelist.item']
        self.start_time = datetime.now()
        self.cr = pooler.get_db(self.dbname).cursor()

        self.pricelistImportID = ids[0]

        self.context = context
        self.error = []
        self.warning = []
        self.first_row = True

        self.uo_new = 0
        self.updated = 0
        self.problems = 0
        self.cache_product = {}

    def run(self):
        # Recupera il record dal database
        self.filedata_obj = self.pool['pricelist.import']
        self.pricelistImportRecord = self.filedata_obj.browse(
            self.cr, self.uid,
            self.pricelistImportID,
            context=self.context
        )
        self.format = self.pricelistImportRecord.format
        self.partner_id = self.pricelistImportRecord.partner_id
        self.file_name = self.pricelistImportRecord.file_name.split('\\')[-1]
        self.pricelist_id = self.pricelistImportRecord.pricelist_id

        Config = getattr(settings, self.pricelistImportRecord.format)
        self.HEADER = Config.HEADER_PRICELIST_ITEM
        self.REQUIRED = Config.REQUIRED_PRICELIST_ITEM

        self.RecordPriceListItem = namedtuple(
            'RecordPriceListItem',
            Config.COLUMNS_PRICELIST_ITEM
        )

        table, self.numberOfLines = import_sheet(
            self.file_name,
            self.pricelistImportRecord.content_text
        )

        if DEBUG:
            # Importa il file
            self.process(self.cr, self.uid, table)

            # Genera il report sull'importazione
            self.notify_import_result(
                self.cr, self.uid,
                self.message_title,
                'Importazione completata',
                record=self.pricelistImportRecord
            )
        else:
            # Elaborazione del file
            try:
                # Importa il listino
                self.process(self.cr, self.uid, table)

                # Genera il report sull'importazione
                self.notify_import_result(
                    self.cr, self.uid,
                    self.message_title,
                    'Importazione completata',
                    record=self.pricelistImportRecord
                )
            except Exception as e:
                # Annulla le modifiche fatte
                self.cr.rollback()
                self.cr.commit()
                title = "Import failed"
                message = "Errore nell'importazione del file %s" % self.file_name + "\nDettaglio:\n\n" + str(e)

                if DEBUG:
                    # Debug
                    _logger.debug(message)
                    pdb.set_trace()

                self.notify_import_result(
                    self.cr, self.uid,
                    title,
                    message,
                    error=True,
                    record=self.pricelistImportRecord
                )

    def process(self, cr, uid, table):
        self.message_title = _("Importazione Pricelist")
        self.progressIndicator = 0

        notifyProgressStep = (self.numberOfLines / 100) + 1
        # NB: divisione tra interi da sempre un numero intero!
        # NB: il + 1 alla fine serve ad evitare divisioni per zero
        # Use counter of processed lines
        # If this line generate an error we will know the right Line Number
        pricelist_version_id = False
        if self.format == 'FormatOne':
            wizard = self.pricelistImportRecord
            # self.browse(cr, uid, ids[0], context=context)

            pricelist_version_id = wizard.pricelist_version_id
            pricelist_version_id.write({
                'items_id': [(2, item.id) for item in pricelist_version_id.items_id]
            })

        for self.processed_lines, row_list in enumerate(table, start=1):

            if not self.import_row(cr, uid, row_list, pricelist_version_id):
                self.problems += 1

            if (self.processed_lines % notifyProgressStep) == 0:
                cr.commit()
                completedQuota = (
                    float(self.processed_lines) / float(self.numberOfLines)
                )
                completedPercentage = math.trunc(completedQuota * 100)
                self.progressIndicator = completedPercentage
                self.updateProgressIndicator(cr, uid, self.pricelistImportID)

        self.progressIndicator = 100
        self.updateProgressIndicator(cr, uid, self.pricelistImportID)
        return True

    def import_row(self, cr, uid, row_list, pricelist_version_id):
        if self.first_row:
            row_str_list = [self.simple_string(value) for value in row_list]
            for column in row_str_list:
                # print column
                if column in self.HEADER:
                    _logger.info(
                        'Riga {0}: Trovato Header'.format(self.processed_lines)
                    )
                    return True
            self.first_row = False

        if not len(row_list) == len(self.HEADER):
            row_str_list = [self.simple_string(value) for value in row_list]
            if DEBUG:
                if len(row_list) > len(self.HEADER):
                    pprint(zip(self.HEADER, row_str_list[:len(self.HEADER)]))
                else:
                    pprint(zip(self.HEADER[:len(row_list)], row_str_list))

            error = u"""
            Row {row}: Row_list is {row_len} long.
            We expect it to be {expected} long, with this columns:
                {keys}
                Instead of this we got this:
                {header}
            """.format(
                row=self.processed_lines,
                row_len=len(row_list),
                expected=len(self.HEADER),
                keys=self.HEADER,
                header=', '.join(row_str_list)
            )

            _logger.error(str(row_list))
            _logger.error(error)
            self.error.append(error)
            return False
        elif DEBUG:
            # pprint(row_list)
            row_str_list = [self.toStr(value) for value in row_list]
            pprint(zip(self.HEADER, row_str_list))
        record = self.RecordPriceListItem._make([self.toStr(value) for value in row_list])

        product = record.code
        if self.format == 'FormatOne':
            if self.cache_product.get(product, False):
                # product_ids = [self.cache_product[product]]
                warning = u'Product {0} already processed in cache'.format(product)
                _logger.warning(warning)
                self.warning.append(warning)
                return False
            else:
                product_ids = self.pool['product.product'].search(cr, uid, [('default_code', '=', product)], context=self.context)
                if not product_ids:
                    product_ids = self.pool['product.product'].search(cr, uid, [('default_code', '=ilike', '%{product}'.format(product=product))], context=self.context)

            if not product_ids:
                error = u'Row {row} => Not Find code: {product}'.format(row=self.processed_lines, product=record.code)
                _logger.error(error)
                self.error.append(error)
                return False

            product_id = product_ids.pop()
            self.cache_product[product] = product_id
            pricelist_version_item_vals = {
                'price_version_id': pricelist_version_id.id,
                'name': record.code,
                'product_id': product_id,
                'base': 1,
                'price_discount': -1,
                'price_surcharge': float(record.price_surcharge) or False
            }

            pricelist_version_item_id = self.pricelist_item_obj.create(cr, uid, pricelist_version_item_vals, self.context)
        elif self.format == 'FormatTwo':

            if self.cache_product.get(product, False):
                # product_ids = [self.cache_product[product]]
                warning = u'Product {0} already processed in cache'.format(product)
                _logger.warning(warning)
                self.warning.append(warning)
                return False
            else:
                supplierinfo_ids = self.pool['product.supplierinfo'].search(cr, uid, [('product_code', '=', product), ('name', '=', self.partner_id.id)], context=self.context)

            if not supplierinfo_ids:
                error = u'Row {row} => Not Find code: {product}'.format(row=self.processed_lines, product=record.code)
                _logger.error(error)
                self.error.append(error)
                return False
            supplierinfo_id = supplierinfo_ids.pop()
            self.cache_product[product] = supplierinfo_id
            supplierinfo = self.pool['product.supplierinfo'].browse(cr, uid, supplierinfo_id, self.context)
            try:
                price_surcharge = float(record.price_surcharge)
            except Exception as e:
                error = u'Row {row} => Error: {error}'.format(row=self.processed_lines, error=e)
                _logger.error(error)
                self.error.append(error)
                return False
            if supplierinfo.pricelist_ids:
                supplierinfo.pricelist_ids[0].write({'price': price_surcharge or 0.0})
            else:
                supplierinfo.write({'pricelist_ids': [(0, 0, {'price': float(record.price_surcharge) or 0.0, 'min_quantity': 0.0})]})

        self.uo_new += 1
        return True
