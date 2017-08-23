# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2015 Andrei Levin (andrei.levin at didotech.com)
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

import netsvc
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
        
        # Inizializzazione classe ImportPricelist
        self.uid = uid
        self.start_time = datetime.now()
        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        self.sale_order_obj = self.pool['sale.order']
        self.sale_order_line_obj = self.pool['sale.order.line']
        self.product_obj = self.pool['product.product']
        self.picking_obj = self.pool['stock.picking']

        # Necessario creare un nuovo cursor per il thread,
        # quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile
        # all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()
        
        self.salesImportID = ids[0]
        
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
    
    def run(self):
        # Recupera il record dal database
        self.filedata_obj = self.pool['sales.import']
        self.salesImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.salesImportID, context=self.context)
        self.file_name = self.salesImportRecord.file_name.split('\\')[-1]
        self.partner_id = self.salesImportRecord.partner_id
        self.date_order = self.salesImportRecord.date_order
        self.origin = self.salesImportRecord.origin or ''
        self.shop_id = self.salesImportRecord.shop_id
        self.location_id = self.salesImportRecord.location_id
        self.auto_approve = self.salesImportRecord.auto_approve
        self.update_price = self.salesImportRecord.update_price

        # ===================================================
        Config = getattr(settings, self.salesImportRecord.format)

        self.HEADER = Config.HEADER_SALES_ITEM
        self.REQUIRED = Config.REQUIRED_SALES_ITEM

        if not len(self.HEADER) == len(Config.COLUMNS_SALES_ITEM.split(',')):
            pprint(zip(self.HEADER, Config.COLUMNS_SALES_ITEM.split(',')))
            raise orm.except_orm('Error: wrong configuration!', 'The length of columns and headers must be the same')
        
        self.RecordSales = namedtuple('RecordSales', Config.COLUMNS_SALES_ITEM)

        # ===================================================

        table, self.numberOfLines = import_sheet(self.file_name, self.salesImportRecord.content_text)

        if DEBUG:
            # Importa il file
            self.process(self.cr, self.uid, table)
            
            # Genera il report sull'importazione
            self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.salesImportRecord)
        else:
            # Elaborazione del file
            try:
                # Importa il sale order
                self.process(self.cr, self.uid, table)
                
                # Genera il report sull'importazione
                self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.salesImportRecord)
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
                
                self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.salesImportRecord)

    def process(self, cr, uid, table):
        self.message_title = _("Importazione Sales")
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
                self.updateProgressIndicator(cr, uid, self.salesImportID)

        # here is import all now need to

        wf_service = netsvc.LocalService("workflow")

        if self.auto_approve:
            for order in self.cache:
                try:
                    wf_service.trg_validate(self.uid, 'sale.order', self.cache[order], 'order_confirm', self.cr)
                    sale_order = self.sale_order_obj.browse(self.cr, self.uid, self.cache[order], self.context)
                    sale_order.manual_invoice()

                    if sale_order.picking_ids:
                        sale_order.picking_ids[0].write({
                            'auto_picking': True,
                        })
                        for move in sale_order.picking_ids[0].move_lines:
                            move.write({
                                'location_id': self.location_id.id
                            })
                        self.picking_obj.force_assign(self.cr, self.uid, [sale_order.picking_ids[0].id])
                except Exception as e:
                    error = "Sale Order {0}: Impossibile da validare {1}".format(self.cache[order], e)
                    _logger.debug(error)
                    self.error.append(error)

        self.progressIndicator = 100
        self.updateProgressIndicator(cr, uid, self.salesImportID)
        
        return True
    
    def import_row(self, cr, uid, row_list):

        if self.first_row:
            row_str_list = [self.simple_string(value) for value in row_list]
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
        record = self.RecordSales._make([self.simple_string(value) for value in row_list])

        for field in self.REQUIRED:
            if not getattr(record, field):
                error = "Riga {0}: Manca il valore della {1}. La riga viene ignorata.".format(self.processed_lines, field)
                _logger.debug(error)
                self.error.append(error)
                return False

        # date = datetime.datetime(*xlrd.xldate_as_tuple(float(record.date), 0)).strftime("%d/%m/%Y %H:%M:%S")
        # date = datetime(*xlrd.xldate_as_tuple(float(record.date), 0)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        client_order_ref = record.location_name.split('.')[0]

        if self.cache.get(client_order_ref):
            sale_id = self.cache[client_order_ref]
            _logger.info(u'Sales {0} already processed in cache'.format(client_order_ref))
        elif self.sale_order_obj.search(cr, uid, [('client_order_ref', '=', client_order_ref), ('state', '=', 'draft'), ('partner_id', '=', self.partner_id.id)]):
            sale_id = self.sale_order_obj.search(cr, uid, [('client_order_ref', '=', client_order_ref), ('state', '=', 'draft'), ('partner_id', '=', self.partner_id.id)])[0]
            self.cache[client_order_ref] = sale_id
            _logger.warning(u'Sales {0} already exist'.format(client_order_ref))
        else:
            # i need to create stock.picking
            # so need to create one
            vals_order = self.sale_order_obj.onchange_partner_id(self.cr, self.uid, [], self.partner_id.id).get('value')
            vals_order.update({
                'partner_id': self.partner_id.id,
                'client_order_ref': self.origin + ': ' + client_order_ref,
                'date_order': self.date_order,
                'shop_id': self.shop_id.id,
                'picking_policy': 'one',
            })
            if self.auto_approve:
                vals_order.update({'order_policy': 'manual'})

            if vals_order.get('sale_agent_ids'):
                del vals_order['sale_agent_ids']

            sale_id = self.sale_order_obj.create(cr, uid, vals_order)
            self.cache[client_order_ref] = sale_id
            _logger.info(u'Create Sale Order {0} '.format(client_order_ref))

        product_id = False
        if hasattr(record, 'item') and record.item:
            product = record.item
            if self.cache_product.get(product):
                product_id = self.cache_product[product]
                _logger.warning(u'Product {0} already processed in cache'.format(product))
            else:
                product_ids = self.product_obj.search(cr, uid, [('default_code', '=', product)])
                if not product_ids:
                    product_ids = self.product_obj.search(cr, uid, [('name', '=', product)])
                    if not product_ids:
                        product_ids = self.product_obj.search(cr, uid, [('ean13', '=', product)])
                if product_ids:
                    product_id = product_ids[0]
                    self.cache_product[product] = product_id
                else:
                    error = u'Row {row}: Product "{product}" not Found'.format(row=self.processed_lines, product=product)
                    _logger.error(error)
                    self.error.append(error)

        if product_id:

            if hasattr(record, 'qty') and record.qty:
                product_qty = float(record.qty)

            if hasattr(record, 'cost') and record.cost:
                cost = float(record.cost)

            # riga
            sale_order = self.sale_order_obj.browse(self.cr, self.uid, sale_id, self.context)
            vals_sale_order_line = self.sale_order_line_obj.product_id_change(self.cr, self.uid, [], sale_order.pricelist_id.id, product_id, qty=0, partner_id=sale_order.partner_id.id).get('value')

            vals_sale_order_line.update({
                'order_id': sale_id,
                'product_id': product_id,
                'product_uom_qty': product_qty,
            })

            if self.update_price:

                list_price_sell = vals_sale_order_line['price_unit']
                price_sell = cost / product_qty

                vals_sale_order_line.update({
                    'discount': (list_price_sell - price_sell) / list_price_sell * 100
                })

            _logger.info(u'Row {row}: Adding product {product} to Sale Order {sale}'.format(row=self.processed_lines, product=record.item, sale=sale_order.name))

            self.sale_order_line_obj.create(cr, uid, vals_sale_order_line, self.context)
            self.uo_new += 1
        else:
            _logger.error(u'Row {row}: Not Find {product}'.format(row=self.processed_lines, product=record.item))

        return product_id
