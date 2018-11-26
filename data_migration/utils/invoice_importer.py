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

import datetime
import logging
import math
import threading
from collections import namedtuple
from datetime import datetime
from pprint import pprint

import netsvc
import pooler
import xlrd
from openerp.addons.core_extended.file_manipulation import import_sheet
from openerp.addons.data_migration import settings
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
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
        self.partner_obj = self.pool['res.partner']
        self.account_invoice_obj = self.pool['account.invoice']
        self.account_invoice_line_obj = self.pool['account.invoice.line']
        self.product_obj = self.pool['product.product']
        self.payment_term_obj = self.pool['account.payment.term']
        self.wf_service = netsvc.LocalService('workflow')

        # Necessario creare un nuovo cursor per il thread,
        # quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile
        # all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()
        
        self.invoiceImportID = ids[0]
        
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
        self.fiscal_position = 1
    
    def run(self):
        # Recupera il record dal database
        self.filedata_obj = self.pool['invoice.import']
        self.invoiceImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.invoiceImportID, context=self.context)
        self.file_name = self.invoiceImportRecord.file_name.split('\\')[-1]
        self.partner_id = self.invoiceImportRecord.partner_id
        self.date_invoice = self.invoiceImportRecord.date_invoice
        self.origin = self.invoiceImportRecord.origin or ''
        self.journal_id = self.invoiceImportRecord.journal_id
        self.location_id = self.invoiceImportRecord.location_id
        self.update_price = self.invoiceImportRecord.update_price
        self.account_id = self.invoiceImportRecord.account_id
        self.type = self.invoiceImportRecord.type
        self.format = self.invoiceImportRecord.format

        # ===================================================
        Config = getattr(settings, self.invoiceImportRecord.format)

        self.HEADER = Config.HEADER_INVOICE_ITEM
        self.REQUIRED = Config.REQUIRED_INVOICE_ITEM

        if not len(self.HEADER) == len(Config.COLUMNS_INVOICE_ITEM.split(',')):
            pprint(zip(self.HEADER, Config.COLUMNS_INVOICE_ITEM.split(',')))
            raise orm.except_orm('Error: wrong configuration!', 'The length of columns and headers must be the same')
        
        self.RecordSales = namedtuple('RecordSales', Config.COLUMNS_INVOICE_ITEM)

        # ===================================================

        try:
            table, self.numberOfLines = import_sheet(self.file_name, self.invoiceImportRecord.content_text)
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
            self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.invoiceImportRecord)

        if DEBUG:
            # Importa il file
            self.process(self.cr, self.uid, table)
            
            # Genera il report sull'importazione
            self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.invoiceImportRecord)
        else:
            # Elaborazione del file
            try:
                # Importa il sale order
                self.process(self.cr, self.uid, table)
                
                # Genera il report sull'importazione
                self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.invoiceImportRecord)
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
                
                self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.invoiceImportRecord)

    def process(self, cr, uid, table):
        self.message_title = _("Import Invoice")
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
                self.updateProgressIndicator(cr, uid, self.invoiceImportID)

        self.progressIndicator = 100
        self.updateProgressIndicator(cr, uid, self.invoiceImportID)
        
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
        record = self.RecordSales._make([self.simple_string(value) for value in row_list])

        for field in self.REQUIRED:
            if not getattr(record, field):
                error = "Riga {0}: Manca il valore della {1}. La riga viene ignorata.".format(self.processed_lines, field)
                _logger.debug(error)
                self.error.append(error)
                return False
        if self.format == 'FormatTwo':
            partner_ids = self.partner_obj.search(cr, uid, [('name', 'like', record.partner_name.split(' ')[1])], context=self.context)
            if partner_ids:
                partner_id = partner_ids[0]
                vals_invoice = {
                    'type': self.type
                }
                vals_invoice.update(self.account_invoice_obj.onchange_journal_id(cr, uid, [], self.journal_id.id, self.context).get('value'))
                vals_invoice.update(self.account_invoice_obj.onchange_partner_id(cr, uid, [], self.type, partner_id, date_invoice=record.date_invoice or '').get('value'))
                vals_invoice.update({
                    'partner_id': partner_id,
                    'name': record.number_invoice.split('.')[0],
                    'internal_number': record.number_invoice.split('.')[0],
                    'date_invoice': datetime(*xlrd.xldate_as_tuple(float(record.date_invoice), 0)).strftime(DEFAULT_SERVER_DATE_FORMAT) or '',
                    'journal_id': self.journal_id.id,
                })

                invoice_id = self.account_invoice_obj.create(cr, uid, vals_invoice, self.context)
                vals_account_invoice_line = {}
                vals_account_invoice_line.update({
                    'name': 'Import Total Amount',
                    'invoice_id': invoice_id,
                    'quantity': 1.0,
                    'account_id': self.account_id.id,
                    'price_unit': record.total_amount or 0.0
                })
                self.account_invoice_line_obj.create(cr, uid, vals_account_invoice_line, self.context)
                _logger.info(u'Row {row}: Adding amount {amount} to Invoice {invoice}'.format(row=self.processed_lines,
                                                                                              amount=record.total_amount,
                                                                                              invoice=invoice_id))
                self.uo_new += 1
            else:
                _logger.warning(u'Row {row}: Not Find {partner}'.format(row=self.processed_lines, partner=record.partner_name))
                invoice_id = False
            return invoice_id

        elif self.format == 'FormatOne':
            name = record.location_name.split('.')[0]

            if self.cache.get(name):
                invoice_id = self.cache[name]
                _logger.info(u'Sales {0} already processed in cache'.format(name))
            elif self.account_invoice_obj.search(cr, uid, [('name', '=', name), ('state', '=', 'draft'), ('partner_id', '=', self.partner_id.id)]):
                invoice_id = self.account_invoice_obj.search(cr, uid, [('name', '=', name), ('state', '=', 'draft'), ('partner_id', '=', self.partner_id.id)])[0]
                self.cache[name] = invoice_id
                _logger.warning(u'Invoice {0} already exist'.format(name))
            else:
                # i need to create invoice
                # so need to create one

                vals_invoice = {
                    'type': self.type
                }
                vals_invoice.update(self.account_invoice_obj.onchange_journal_id(cr, uid, [], self.journal_id.id, self.context).get('value'))
                vals_invoice.update(self.account_invoice_obj.onchange_partner_id(cr, uid, [], self.type, self.partner_id.id, date_invoice=self.date_invoice).get('value'))
                vals_invoice.update({
                    'partner_id': self.partner_id.id,
                    'name': self.origin + ': ' + name,
                    'date_invoice': self.date_invoice,
                    'journal_id': self.journal_id.id,
                })

                if self.location_id:
                    vals_invoice.update({
                        'location_id': self.location_id.id,
                        'move_products': True,
                    })

                if vals_invoice.get('sale_agent_ids'):
                    del vals_invoice['sale_agent_ids']

                invoice_id = self.account_invoice_obj.create(cr, uid, vals_invoice, self.context)
                self.cache[name] = invoice_id
                _logger.info(u'Create Invoice {0} on Draft '.format(name))
                self.fiscal_position = vals_invoice['fiscal_position']
            product_id = False
            if hasattr(record, 'item') and record.item:
                product = record.item
                if self.cache_product.get(product):
                    product_id = self.cache_product[product]
                    _logger.warning(u'Product {0} already processed in cache'.format(product))
                else:
                    product_ids = self.product_obj.search(cr, uid, [('default_code', '=', product)], context=self.context)
                    if not product_ids:
                        product_ids = self.product_obj.search(cr, uid, [('name', '=', product)], context=self.context)
                        if not product_ids:
                            product_ids = self.product_obj.search(cr, uid, [('ean13', '=', product)], context=self.context)
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
                vals_account_invoice_line = self.account_invoice_line_obj.product_id_change(cr, uid, [], product_id, 1, qty=product_qty, name='', type=self.type, partner_id=self.partner_id.id, fposition_id=self.fiscal_position, price_unit=False, address_invoice_id=False, currency_id=False, context=None, company_id=None).get('value')

                vals_account_invoice_line.update({
                    'invoice_id': invoice_id,
                    'product_id': product_id,
                    'quantity': product_qty,
                })

                if self.update_price:
                    price_sell = cost / product_qty
                    vals_account_invoice_line.update({
                         'price_unit': price_sell,
                         'discount': 0,
                    })
                    # list_price_sell = vals_account_invoice_line['price_unit']
                    # price_sell = cost / product_qty
                    #
                    # vals_account_invoice_line.update({
                    #     'discount': (list_price_sell - price_sell) / list_price_sell * 100
                    # })
                _logger.info(u'Row {row}: Adding product {product} to Invoice {invoice}'.format(row=self.processed_lines, product=record.item, invoice=invoice_id))

                self.account_invoice_line_obj.create(cr, uid, vals_account_invoice_line, self.context)
                self.uo_new += 1
            else:
                _logger.warning(u'Row {row}: Not Found {product}'.format(row=self.processed_lines, product=record.item))
                invoice_id = False
            return invoice_id
        elif self.format == 'FormatThree':
            partner_code = record.partner_code
            number = record.number_invoice.split('.')[0]
            invoice_ids = self.account_invoice_obj.search(cr, uid, [('number', '=', number)], context=self.context)
            if invoice_ids:
                return invoice_ids[0]
            partner_ids = self.partner_obj.search(cr, uid, ['|', ('property_supplier_ref', '=', partner_code), ('property_customer_ref', '=', partner_code)], context=self.context)
            if partner_ids:
                validation_check = True
                partner_id = partner_ids[0]
                vals_invoice = {
                    'type': self.type
                }
                vals_invoice.update(self.account_invoice_obj.onchange_journal_id(cr, uid, [], self.journal_id.id, self.context).get('value'))
                if record.date_invoice:
                    date_invoice = datetime(*xlrd.xldate_as_tuple(float(record.date_invoice), 0)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                else:
                    date_invoice = ''
                vals_invoice.update(self.account_invoice_obj.onchange_partner_id(cr, uid, [], self.type, partner_id, date_invoice=date_invoice or '').get('value'))


                payment_term_ids = self.payment_term_obj.search(cr, uid, [('code', '=', record.payment_code)], context=self.context)
                if payment_term_ids:
                    vals_invoice['payment_term'] = payment_term_ids[0]
                else:
                    error = u'Row {row}: Invoice {invoice} Not find Payment Term {payment_term} {name}'.format(row=self.processed_lines, invoice=record.number_invoice, payment_term=record.payment_code, name=record.payment_name)
                    _logger.error(error)
                    self.error.append(error)
                    validation_check = False

                account_id = self.account_id and self.account_id.id or False
                vals_account_invoice_line = self.account_invoice_line_obj.default_get(cr, uid, [], context={'type': self.type, 'fiscal_position': vals_invoice['fiscal_position']})
                vals_account_invoice_line.update(self.account_invoice_line_obj.product_id_change(cr, uid, [], False, False, qty=0, name='', type=self.type, partner_id=partner_id, fposition_id=vals_invoice['fiscal_position'], price_unit=False, address_invoice_id=False, currency_id=False, context=self.context, company_id=None).get('value'))
                if account_id:
                    vals_account_invoice_line['account_id'] = account_id
                # if vals_account_invoice_line.get('invoice_line_tax_id', False):
                #     tax_tab = [(6, 0, vals_account_invoice_line['invoice_line_tax_id'])]
                #     vals_account_invoice_line['invoice_line_tax_id'] = tax_tab

                vals_account_invoice_line.update({
                    'name': _('Import Total Amount'),
                    'quantity': 1.0,
                    'price_unit': record.total_untax or 0.0
                })

                vals_invoice.update({
                    'partner_id': partner_id,
                    'name': record.number_invoice.split('.')[0],
                    'internal_number': record.number_invoice.split('.')[0],
                    'date_invoice': date_invoice,
                    'journal_id': self.journal_id.id,
                    'invoice_line': [(0, 0, vals_account_invoice_line)]
                })

                invoice_id = self.account_invoice_obj.create(cr, uid, vals_invoice, self.context)
                invoice = self.account_invoice_obj.browse(cr, uid, invoice_id, context=self.context)
                invoice.button_reset_taxes()
                _logger.info(u'Row {row}: Adding amount {amount} to Invoice {invoice}'.format(row=self.processed_lines,
                                                                                              amount=record.total_untax,
                                                                                              invoice=invoice_id))
                amount_tax = invoice.amount_tax
                if amount_tax == float(record.total_tax):
                    _logger.info(u'Row {row}: Validation to Invoice {invoice}'.format(row=self.processed_lines, invoice=invoice_id))
                else:
                    validation_check = False
                    error = u'Row {row}: Invoice {invoice} have different tax amout {amount_tax} != {file}'.format(row=self.processed_lines, invoice=record.number_invoice, amount_tax=amount_tax, file=record.total_tax)
                    _logger.error(error)
                    self.error.append(error)
                if validation_check:
                    try:
                        self.wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                    except Exception as e:
                        error = u'Row {row}: Invoice {invoice} get Error {error}'.format(
                            row=self.processed_lines, invoice=record.number_invoice, error=e)
                        _logger.error(error)
                        self.error.append(error)
                self.uo_new += 1
            else:
                error = u'Row {row}: Not Find {partner}'.format(row=self.processed_lines, partner=record.partner_name)
                _logger.error(error)
                self.error.append(error)
                invoice_id = False
            return invoice_id
