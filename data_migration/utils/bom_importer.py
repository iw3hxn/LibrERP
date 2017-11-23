# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

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

DEBUG = settings.DEBUG

if DEBUG:
    import pdb


class ImportFile(threading.Thread, Utils):
    def __init__(self, cr, uid, ids, context):
        # Inizializzazione superclasse
        threading.Thread.__init__(self)

        # Inizializzazione classe
        self.uid = uid
        self.start_time = datetime.now()
        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        self.product_obj = self.pool['product.product']
        self.supplierinfo_obj = self.pool['product.supplierinfo']
        self.bom_obj = self.pool['mrp.bom']

        # Necessario creare un nuovo cursor per il thread, quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()

        self.bomImportID = ids[0]

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
        self.filedata_obj = self.pool['bom.import']
        self.bomImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.bomImportID, context=self.context)
        self.file_name = self.bomImportRecord.file_name.split('\\')[-1]

        self.update_product_name = self.bomImportRecord.update_product_name

        # ===================================================
        Config = getattr(settings, self.bomImportRecord.format)

        self.HEADER = Config.HEADER_BOM
        self.REQUIRED = Config.REQUIRED_BOM
        self.BOM_PRODUCT_SEARCH = Config.BOM_PRODUCT_SEARCH
        self.BOM_SEARCH = Config.BOM_SEARCH
        # self.BOM_WARNINGS = Config.BOM_WARNINGS
        # self.BOM_ERRORS = Config.BOM_ERRORS

        # Default values
        self.BOM_DEFAULTS = Config.BOM_DEFAULTS
        self.FORMAT = self.bomImportRecord.format

        if not len(self.HEADER) == len(Config.COLUMNS_BOM.split(',')):
            pprint(zip(self.HEADER, Config.COLUMNS_BOM.split(',')))
            raise orm.except_orm('Error: wrong configuration!', 'The length of columns and headers must be the same')

        self.RecordBom = namedtuple('RecordBom', Config.COLUMNS_BOM)

        # ===================================================
        try:
            table, self.numberOfLines = import_sheet(self.file_name, self.bomImportRecord.content_text)
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
            self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.bomImportRecord)

        if DEBUG:
            # Importa il listino
            self.process(self.cr, self.uid, table)

            # Genera il report sull'importazione
            self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.bomImportRecord)
        else:
            # Elaborazione del listino prezzi
            try:
                # Importa il listino
                self.process(self.cr, self.uid, table)

                # Genera il report sull'importazione
                self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.bomImportRecord)
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

                self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.bomImportRecord)

    def get_uom(self, cr, uid, name):
        translate = {
            'm': 'm',
            'kgm': 'kg',
            'unit': 'Unit(s)',
            'litre': 'Liter(s)',
            'LT': 'Litre',
            'lt': 'Litre',
            '20 lt': 'Litre',
            'PCE': 'PCE',
            'Pz.': 'PCE',
            'PZ': 'PCE',
            'Pa.': 'PCE',  # Paia
            'Paia': 'PCE',  # Paia
            'CF': 'PCE',
            'N.': 'PCE',
            'Mt.': 'PCE',
            'pz': 'PCE',
            'copp': 'PCE',
            'conf': 'PCE',
            'Kit': 'PCE',
            'Pacco': 'PCE',
            'scat': 'PCE',
            'pac': 'PCE',
            'HH': 'Hour',
            'M': 'm',
            'ML.': 'm',
            'mc': 'mq',
            'M2': 'mq',
            'mq': 'mq',
            'Kg': 'kg',
            'kg': 'kg'
        }

        if name and len(name) > 20 and name[:20] == 'product.product_uom_':
            uom_name = name[20:]
        elif name:
            uom_name = name
        else:
            error = "Row {0}: Can't find valid UOM".format(self.processed_lines)
            _logger.error(error)
            self.error.append(error)
            return False
        if uom_name not in translate:
            warning = "Row {0}: Can't find valid UOM {1}".format(self.processed_lines, name)
            _logger.warning(warning)
            self.warning.append(warning)
            return self.pool['product.product'].default_get(cr, uid, ['uom_id'], context=self.context)['uom_id']
        uom_ids = self.pool['product.uom'].search(cr, uid, [('name', '=ilike', translate[uom_name])], context=self.context)
        if len(uom_ids) == 1:
            return uom_ids[0]
        elif len(uom_ids) > 1:
            error = "Row {0}: Abnormal situation. More than one UOM '{1}' found".format(self.processed_lines, uom_name)
            _logger.error(error)
            self.error.append(error)
            return False
        else:
            error = "Row {0}: UOM '{1}' is missing in database".format(self.processed_lines, uom_name)
            _logger.error(error)
            self.error.append(error)
            return False

    def create_bom(self, cr, uid, product_id, product_vals_bom, record):
        product = self.product_obj.browse(cr, uid, product_id, context=self.context)
        product_onchange = self.bom_obj.onchange_product_id(cr, uid, self.bomImportID, product.id, product.name,
                                                            context=self.context).get('value')
        product_vals_bom.update({
            'product_id': product.id,
            'name': product_onchange['name'],
            'product_uom': product_onchange['product_uom']
        })

        if hasattr(record, 'bom_code'):
            product_vals_bom['code'] = getattr(record, 'bom_code')

        sub_item_ids = self.product_obj.search(cr, uid, [
            (self.BOM_PRODUCT_SEARCH, '=', record.sub_item_code)
        ], context=self.context)
        if sub_item_ids:
            bom_lines = self.bom_obj.default_get(
                cr, uid,
                [
                    'product_qty', 'type', 'company_id', 'sequence', 'product_rounding',
                    'active', 'product_efficiency'
                ], self.context
            )
            sub_item = self.product_obj.browse(cr, uid, sub_item_ids[0], context=self.context)
            # sub_item_onchange = self.bom_obj.onchange_product_id(cr, uid, self.bomImportID, sub_item.id, sub_item.name,
            #                                                      context=self.context).get('value')
            bom_lines.update({
                'product_id': sub_item.id,
                # 'name': sub_item_onchange['name'],
                'name': sub_item.name,
                # 'product_uom': sub_item_onchange['product_uom']
                'product_uom': sub_item.uom_id.id,
                'code': getattr(record, 'bom_code', False)
            })

            if hasattr(record, 'product_qty') and record.product_qty:
                if self.FORMAT == 'FormatOmnitron':
                    if sub_item.weight_per_meter:
                        bom_lines['product_qty'] = abs(float(record.product_qty)) * 1000
                    else:
                        bom_lines['product_qty'] = abs(float(record.product_qty))
                else:
                    bom_lines['product_qty'] = abs(float(record.product_qty))

            if hasattr(record, 'observation') and record.observation:
                bom_lines['position'] = record.observation

            domain = [
                ('product_id', '=', product.id),
                ('bom_id', '=', None)
            ]

            if bom_lines.get('code', False):
                domain.append(('code', '=', bom_lines['code']))

            product_bom_ids = self.bom_obj.search(cr, uid, domain, context=self.context)

            if product_bom_ids:
                product_bom_id = product_bom_ids[0]
                self.bom_obj.write(cr, uid, product_bom_id, product_vals_bom, self.context)
                self.updated += 1

                sub_item_bom_ids = self.bom_obj.search(cr, uid, [('product_id', '=', sub_item.id),
                                                                 ('bom_id', '=', product_bom_id)], context=self.context)
                bom_lines.update({'bom_id': product_bom_id})
                if sub_item_bom_ids:
                    if hasattr(record, 'name') and record.name:
                        sub_item_boms = self.bom_obj.browse(cr, uid, sub_item_bom_ids, context=self.context)
                        if hasattr(record, 'observation') and record.observation:
                            ins_bom = True
                            for sub_item_bom in sub_item_boms:
                                if record.observation == sub_item_bom.position:
                                    bom_lines_copy = bom_lines.copy()
                                    bom_lines_copy.update({})
                                    self.bom_obj.write(cr, uid, sub_item_bom.id, bom_lines_copy, self.context)
                                    self.updated += 1
                                    ins_bom = False

                            if ins_bom:
                                bom_lines.update({'position': record.observation})
                                sub_item_bom_id = self.bom_obj.create(cr, uid, bom_lines, self.context)
                                self.uo_new += 1
                    else:
                        sub_item_bom_id = sub_item_bom_ids[0]
                        self.bom_obj.write(cr, uid, sub_item_bom_id, bom_lines, self.context)
                        self.updated += 1
                else:
                    sub_item_bom_id = self.bom_obj.create(cr, uid, bom_lines, self.context)
                    self.uo_new += 1
            else:
                product_bom_id = self.bom_obj.create(cr, uid, product_vals_bom, self.context)
                self.uo_new += 1
                bom_lines.update({'bom_id': product_bom_id})
                sub_item_bom_id = self.bom_obj.create(cr, uid, bom_lines, self.context)
                self.uo_new += 1
            # return True
        else:
            error = 'Product: {code} is not present in DB.'.format(code=record.sub_item_code)
            if error not in self.error:
                _logger.debug(error)
                self.error.append(error)
            return False

    def get_product_ids(self, cr, uid, record):
        """For Omnitron format Only!"""
        omnicode = '{:0>9d}'.format(int(getattr(record, self.BOM_PRODUCT_SEARCH)))
        product_ids = self.product_obj.search(cr, uid, [
            (self.BOM_PRODUCT_SEARCH, '=', omnicode)
        ], context=self.context)
        if product_ids:
            self.product_obj.write(
                cr, uid, product_ids, {
                    'name': record.product_description,
                    'old_code': '{}:{}'.format(omnicode, record.bom_code)
                },
                context=self.context
            )
        else:
            product_ids = self.product_obj.search(cr, uid, [
                (self.BOM_PRODUCT_SEARCH, '=', '{}:{}'.format(omnicode, record.bom_code))
            ], context=self.context)

            if product_ids:
                self.product_obj.write(
                    cr, uid, product_ids, {
                        'name': record.product_description,
                        'old_code': '{}:{}'.format(omnicode, record.bom_code)
                    },
                    context=self.context
                )
            else:
                product_ids = self.product_obj.search(cr, uid, [
                    (self.BOM_PRODUCT_SEARCH, '=ilike', '{}%'.format(omnicode))
                ], context=self.context)
                if product_ids:
                    product_id = self.product_obj.copy(cr, uid, product_ids[0], {
                        'name': record.product_description,
                        'old_code': '{}:{}'.format(omnicode, record.bom_code),
                        'bom_ids': []
                    })
                    product_ids = [product_id]
                else:
                    product_ids = False
        return product_ids

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
                """.format(row=self.processed_lines, row_len=len(row_list), expected=len(self.HEADER), keys=self.HEADER, header=', '.join(map(lambda s: s or '', row_str_list)))

            _logger.error(str(row_list))
            _logger.error(error)
            self.error.append(error)
            return False
        elif DEBUG:
            # pprint(row_list)
            row_str_list = [self.toStr(value) for value in row_list]
            pprint(zip(self.HEADER, row_str_list))

        # Sometime value is only numeric and we don't want string to be treated as Float
        record = self.RecordBom._make([self.toStr(value) for value in row_list])

        for field in self.REQUIRED:
            if not getattr(record, field):
                error = "Riga {0}: Manca il valore della {1}. La riga viene ignorata.".format(self.processed_lines, field)
                _logger.debug(error)
                self.error.append(error)
                return False

        # Start values collection
        # ------------------------------------------------------------------------
        product_flag = True
        product_vals = {}

        if hasattr(record, 'old_code') and record.old_code:
            product_vals['old_code'] = record.old_code

        if hasattr(record, 'name') and record.name:
            product_vals['name'] = record.name

            if hasattr(record, 'default_code') and record.default_code:
                product_vals['default_code'] = record.default_code
            else:
                product_flag = False

            if product_flag:
                product_vals.update({
                    'sale_ok': True,
                    'purchase_ok': False
                })
        else:
            product_flag = False

        if self.FORMAT == 'FormatOmnitron':
            product_ids = self.get_product_ids(cr, uid, record)
        else:
            product_ids = self.product_obj.search(cr, uid, [
                (self.BOM_PRODUCT_SEARCH, '=', getattr(record, self.BOM_PRODUCT_SEARCH))
            ], context=self.context)

        if product_ids:
            product_id = product_ids[0]
            if product_flag:
                self.product_obj.write(cr, uid, product_id, product_vals, self.context)
                self.updated += 1
        else:
            if product_flag:
                product_id = self.product_obj.create(cr, uid, product_vals, self.context)
                self.uo_new += 1
            else:
                error = 'Errore linea: {line}. Manca il nome o il codice del prodotto identificato da {code}'.format(
                    line=self.processed_lines,
                    code=getattr(record, self.BOM_PRODUCT_SEARCH)
                )
                if error not in self.error:
                    _logger.debug(error)
                    self.error.append(error)
                return False

        sub_item_flag = True
        product_vals = {}

        sub_product_ids = self.product_obj.search(cr, uid, [
            (self.BOM_PRODUCT_SEARCH, '=', record.sub_item_code)
        ], context=self.context)

        if hasattr(record, 'name') and record.name:
            if hasattr(record, 'sub_item_code') and record.sub_item_code:
                product_vals.update({self.BOM_PRODUCT_SEARCH: record.sub_item_code})
            else:
                sub_item_flag = False

            if hasattr(record, 'standard_price') and record.standard_price:
                product_vals.update({'standard_price': record.standard_price})
            else:
                product_vals.update({'standard_price': 0})

            if sub_item_flag:
                product_vals.update({
                    'sale_ok': False,
                    'purchase_ok': False,
                })
        else:
            sub_item_flag = False

        if sub_product_ids:
            if sub_item_flag:
                if hasattr(record, 'sub_description') and record.sub_description:
                    product_vals.update({'name': record.sub_description})
                if hasattr(record, 'sub_dimension') and record.sub_dimension:
                    product_vals.update({'measures': record.sub_dimension})
                if hasattr(record, 'uom_maga') and record.uom_maga:
                    product_vals['uom_id'] = self.get_uom(cr, uid,
                                                          record.uom_maga)  # todo better, is on product_importer
                    product_vals['uom_po_id'] = product_vals['uom_id']

                # Update Sub product
                self.product_obj.write(cr, uid, sub_product_ids[0], product_vals, self.context)
                self.updated += 1
        else:
            if hasattr(record, 'sub_description') and record.sub_description:
                sub_item_flag = True
                product_vals.update({'name': record.sub_description})
            else:
                sub_item_flag = False
            if hasattr(record, 'sub_dimension') and record.sub_dimension:
                product_vals.update({'measures': record.sub_dimension})

            if sub_item_flag:
                sub_product_ids = [self.product_obj.create(cr, uid, product_vals, self.context)]
                self.uo_new += 1
            else:
                error = 'Errore linea: {line}. Manca il nome, il codice del (sub) prodotto identificato da {code}'.format(
                    line=self.processed_lines,
                    code=record.sub_item_code
                )
                if error not in self.error:
                    _logger.debug(error)
                    self.error.append(error)
                return False

        product_vals_bom = self.bom_obj.default_get(
            cr, uid, [
                'product_qty', 'type', 'company_id', 'sequence', 'product_rounding', 'active', 'product_efficiency'
            ],
            self.context
        )

        # if product_id:

        # if self.FORMAT == 'FormatOmnitron':
        #
        #     self.create_omnitron_bom(cr, uid, product_id, product_vals_bom, record)
        # else:
        self.create_bom(cr, uid, product_id, product_vals_bom, record)

        # else:
        #     error = 'Prodotto: {code} non presente nel DB.'.format(code=record.default_code)
        #     if error not in self.error:
        #         _logger.debug(error)
        #         self.error.append(error)
        #     return False
        return True

    def process(self, cr, uid, table):
        self.message_title = _("Importazione Distinta Base")
        self.progressIndicator = 0

        notifyProgressStep = (self.numberOfLines / 100) + 1  # NB: divisione tra interi da sempre un numero intero!
        # NB: il + 1 alla fine serve ad evitare divisioni per zero

        # Use counter of processed lines
        # If this line generate an error we will know the right Line Number
        for self.processed_lines, row_list in enumerate(table, start=1):
            if not self.import_row(cr, uid, row_list):
                self.problems += 1

            _logger.debug('>> {}'.format(self.processed_lines))

            if (self.processed_lines % notifyProgressStep) == 0:
                cr.commit()
                completedQuota = float(self.processed_lines) / float(self.numberOfLines)
                completedPercentage = math.trunc(completedQuota * 100)
                self.progressIndicator = completedPercentage
                self.updateProgressIndicator(cr, uid, self.bomImportID)

        self.progressIndicator = 100
        self.updateProgressIndicator(cr, uid, self.bomImportID)

        return True
