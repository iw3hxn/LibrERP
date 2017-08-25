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

import pooler
from openerp.addons.core_extended.file_manipulation import import_sheet
# import data_migration.settings as settings
from openerp.addons.data_migration import settings
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from product.product import check_ean
from tools.translate import _
from tools import ustr
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
        self.supplierinfo_obj = self.pool['product.supplierinfo']

        # Necessario creare un nuovo cursor per il thread,
        # quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile
        # all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()

        self.productImportID = ids[0]

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
        self.filedata_obj = self.pool['product.import']
        self.productImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.productImportID, context=self.context)
        self.file_name = self.productImportRecord.file_name.split('\\')[-1]

        self.update_product_name = self.productImportRecord.update_product_name

        # ===================================================
        Config = getattr(settings, self.productImportRecord.format)
        self.FORMAT = self.productImportRecord.format
        self.HEADER = Config.HEADER_PRODUCT
        self.REQUIRED = Config.REQUIRED_PRODUCT
        self.PRODUCT_SEARCH = Config.PRODUCT_SEARCH
        self.PRODUCT_WARNINGS = Config.PRODUCT_WARNINGS
        self.PRODUCT_ERRORS = Config.PRODUCT_ERRORS

        # Default values
        self.PRODUCT_DEFAULTS = Config.PRODUCT_DEFAULTS

        if not len(self.HEADER) == len(Config.COLUMNS_PRODUCT.split(',')):
            pprint(zip(self.HEADER, Config.COLUMNS_PRODUCT.split(',')))
            raise orm.except_orm('Error: wrong configuration!', 'The length of columns and headers must be the same')

        self.RecordProduct = namedtuple('RecordProduct', Config.COLUMNS_PRODUCT)

        # ===================================================
        try:
            table, self.numberOfLines = import_sheet(self.file_name, self.productImportRecord.content_text)
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
            self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.productImportRecord)

        if DEBUG:
            # Importa il listino
            self.process(self.cr, self.uid, table)

            # Genera il report sull'importazione
            self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.productImportRecord)
        else:
            # Elaborazione del listino prezzi
            try:
                # Importa il listino
                self.process(self.cr, self.uid, table)

                # Genera il report sull'importazione
                self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata', record=self.productImportRecord)
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

                self.notify_import_result(self.cr, self.uid, title, message, error=True, record=self.productImportRecord)

    def process(self, cr, uid, table):
        self.message_title = _("Importazione prodotti")
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
                self.updateProgressIndicator(cr, uid, self.productImportID)

        self.progressIndicator = 100
        self.updateProgressIndicator(cr, uid, self.productImportID)

        return True

    def get_category(self, cr, uid, categories, parent_id=False):

        if isinstance(categories, (unicode, str)):
            categories = [categories]

        if categories:
            if DEBUG:
                print(categories)
            category_obj = self.pool['product.category']
            name = categories.pop(0)
            category_ids = category_obj.search(cr, uid, [('name', '=', name.strip()), ('parent_id', '=', parent_id)], context=self.context)

            if len(category_ids) == 1:
                if categories:
                    return self.get_category(cr, uid, categories, parent_id=category_ids[0])
                else:
                    return category_ids[0]
            elif len(category_ids) > 1:
                error = "Row {0}: Abnormal situation. More than one category '{1}' found".format(self.processed_lines, name)
                _logger.error(error)
                self.error.append(error)
                return False
            else:
                # error = "Row {0}: Category '{1}' is missing in database".format(self.processed_lines, name)
                # _logger.error(error)
                # self.error.append(error)
                # return False
                category_id = category_obj.create(cr, uid, {'name': name.strip(), 'parent_id': parent_id}, context=self.context)

                if categories:
                    return self.get_category(cr, uid, categories, category_id)
                else:
                    return category_id

        return False

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
            'Pa.': 'PCE',  # Paia
            'Paia': 'PCE',  # Paia
            'PZ': 'PCE',
            'Pz': 'PCE',
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
            'mc': 'm',
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

    def get_taxes(self, cr, uid, description):
        tax_obj = self.pool['account.tax']

        tax_ids = tax_obj.search(cr, uid, [('description', '=', description)], context=self.context)

        if len(tax_ids) == 1:
            return tax_ids
        elif len(tax_ids) > 1:
            error = "Row {0}: Abnormal situation. More than one tax '{1}' found".format(self.processed_lines, description)
            _logger.error(error)
            self.error.append(error)
            return False
        else:
            error = "Row {0}: Tax '{1}' is missing in database".format(self.processed_lines, description)
            _logger.error(error)
            self.error.append(error)
            return False

    def get_suppliers(self, cr, uid, names):
        names = names.split(',')
        supplier_ids = []

        for name in names:
            name = name.strip()
            partner_ids = self.pool['res.partner'].search(cr, uid, [('name', '=ilike', name), ('supplier', '=', True)], context=self.context)

            if len(partner_ids) == 1:
                supplier_ids += partner_ids
            elif len(supplier_ids) > 1:
                warning = "Row {0}: Abnormal situation. More than one supplier '{1}' found".format(self.processed_lines, name)
                _logger.warning(warning)
                self.warning.append(warning)
                return False
            else:
                warning = "Row {0}: Supplier '{1}' is missing in database".format(self.processed_lines, name)
                _logger.warning(warning)
                self.warning.append(warning)
                return False

        return supplier_ids

    def get_brand(self, cr, uid, name):
        brand_obj = self.pool['product.brand']
        brand_ids = brand_obj.search(cr, uid, [('name', '=ilike', name)], context=self.context)

        if len(brand_ids) == 1:
            return brand_ids[0]
        elif len(brand_ids) > 1:
            warning = "Row {0}: Abnormal situation. More than one brand '{1}' found".format(self.processed_lines, name)
            _logger.warning(warning)
            self.warning.append(warning)
            return False
        else:
            return brand_obj.create(cr, uid, {'name': name}, context=self.context)

    def get_order_duration(self, cr, uid, name):
        # (CM= canone mensile, UT= unatantum, CA= Canone annuale, CT = canone trimestrale, CS = canone semestrale, CQ= canone quadrimestrale)
        translate = {
            'CM': 30,
            'CT': 90,
            'CQ': 120,
            'CS': 180,
            'CA': 365,
        }

        res = {
            'subscription': False,
            'order_duration': False
        }

        if translate.get(name, False):
            res = {
                'subscription': True,
                'order_duration': translate[name],
            }
        return res

    def set_product_qty(self, cr, uid, product_id, new_quantity, context=None):
        """
        This function is adopted from stock wizard stock.change.product.qty

        Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param product_id: Product
        @param new_quantity
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        inventry_obj = self.pool['stock.inventory']
        inventry_line_obj = self.pool['stock.inventory.line']
        product_obj = self.pool['product.product']
        location_obj = self.pool['stock.location']

        product = product_obj.browse(cr, uid, product_id, context=context)

        if new_quantity < 0:
            warning = _('Quantity cannot be negative.')
            _logger.warning(warning)
            self.warning.append(warning)
            return False
        else:
            location_ids = location_obj.search(cr, uid, [('name', '=', 'Stock')])

            inventory_id = inventry_obj.create(
                cr, uid, {'name': _('INV: %s') % ustr(product.name)}, context=context
            )
            line_data = {
                'inventory_id': inventory_id,
                'product_qty': new_quantity,
                'location_id': location_ids and location_ids[0],
                'product_id': product_id,
                'product_uom': product.uom_id.id,
                # 'prod_lot_id': data.prodlot_id.id
            }
            inventry_line_obj.create(cr, uid, line_data, context=context)

            inventry_obj.action_confirm(cr, uid, [inventory_id], context=context)
            inventry_obj.action_done(cr, uid, [inventory_id], context=context)

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
        record = self.RecordProduct._make([self.toStr(value) for value in row_list])
        print record

        identifier_field = self.PRODUCT_SEARCH[0]
        identifier = getattr(record, identifier_field).strip()

        # # Look for duplicated default code
        # if record.default_code and record.default_code.strip() in self.cache:
        #     _logger.warning(u'Code {0} already processed'.format(record.default_code.strip()))
        #     # return False
        # elif record.default_code:
        #     self.cache.append(record.default_code.strip())

        # Look for duplicated default code
        if identifier and identifier in self.cache:
            _logger.warning(u'Code {0} already processed'.format(identifier))
            # return False
        elif identifier:
            self.cache.append(identifier)

        for field in self.REQUIRED:
            if not getattr(record, field):
                error = "Riga {0}: Manca il valore della {1}. La riga viene ignorata.".format(self.processed_lines, field)
                _logger.debug(error)
                self.error.append(error)
                return False

        # print '>>>>>>>', record.name
        vals_product = self.product_obj.default_get(cr, uid, [
            'taxes_id',
            'supplier_taxes_id',
            'property_account_income',
            'property_account_expense'
        ], self.context)

        if vals_product.get('taxes_id'):
            vals_product['taxes_id'] = [(6, 0, vals_product.get('taxes_id'))]
        if vals_product.get('supplier_taxes_id'):
            vals_product['supplier_taxes_id'] = [(6, 0, vals_product.get('supplier_taxes_id'))]

        # Check if there are fields that require special treatment:
        if self.FORMAT == 'FormatOmnitron':
            # TODO: description_english

            if record.omnitron_procurement == 'PRODOTTO NON DI MAGAZZINO':
                vals_product.update({
                    'type': 'product',
                    'procure_method': 'make_to_order'
                })
            elif record.omnitron_procurement == 'PRODOTTO NORMALMENTE A MAGAZZINO':
                vals_product.update({
                    'type': 'product',
                    'procure_method': 'make_to_stock'
                })
            elif record.omnitron_procurement == 'PRODOTTO NOT GESTITO A MAGAZZINO':
                vals_product.update({
                    'type': 'service',
                    'procure_method': 'make_to_order'
                })

            if not record.omnitron_produce_delay == '\N':
                produce_delay = {
                    '3 Day': 3,
                    '7 Days': 7,
                    '20 Days': 20
                }
                vals_product['produce_delay'] = produce_delay[record.omnitron_produce_delay]

            vals_product.update({
                'name': record.description.split('\\')[0],
                'old_code': record.old_code,
                'delivery_cost': record.omnitron_delivery_cost or 0.0,
                'weight_per_meter': record.omnitron_weight_per_meter
            })
        elif isinstance(record.name, unicode):
            vals_product['name'] = record.name
        else:
            vals_product['name'] = unicode(record.name, 'utf-8')

        for field in self.PRODUCT_SEARCH:
            if hasattr(record, field) and getattr(record, field):
                vals_product[field] = getattr(record, field)
                break
        else:
            error = "Row {0}: Can't find valid product key".format(self.processed_lines)
            _logger.error(error)
            self.error.append(error)
            return False

        if hasattr(record, 'category') and record.category:
            if '\\' in record.category:
                categories = record.category.split('\\')
            elif '/' in record.category:
                categories = record.category.split('/')
            else:
                categories = record.category
            vals_product['categ_id'] = self.get_category(cr, uid, categories)

        if hasattr(record, 'brand') and record.brand:
            vals_product['product_brand_id'] = self.get_brand(cr, uid, record.brand)

        if hasattr(record, 'order_duration') and record.order_duration:
            subscription = self.get_order_duration(cr, uid, record.order_duration)
            vals_product.update(subscription)

        if hasattr(record, 'description') and record.description:
            if isinstance(record.description, unicode):
                description = record.description
            else:
                description = unicode(record.description, 'utf-8')
            vals_product['description'] = description

        if hasattr(record, 'description_sale') and record.description_sale:
            if isinstance(record.description_sale, unicode):
                description_sale = record.description_sale
            else:
                description_sale = unicode(record.description_sale, 'utf-8')
            vals_product['description_sale'] = description_sale

        if hasattr(record, 'uom') and record.uom:
            vals_product['uom_id'] = self.get_uom(cr, uid, record.uom)
            vals_product['uom_po_id'] = vals_product['uom_id']
        # else:
        #     if hasattr(record, 'uom_po_id') and record.uom_po_id:
        #         vals_product['uom_po_id'] = self.get_uom(cr, uid, record.uom_po_id)
        #         vals_product['uom_po_id'] = record.uom_po_id

        if hasattr(record, 'active') and record.active:
            if record.active == 'FALSE':
                vals_product['active'] = False

            if record.active == 'Y':
                vals_product['active'] = True
            elif record.active == 'N':
                vals_product['active'] = False

        if hasattr(record, 'procure_method') and record.procure_method:
            if record.procure_method.lower() == 'make to stock':
                vals_product['procure_method'] = 'make_to_stock'
            if record.procure_method.lower() == 'make to order':
                vals_product['procure_method'] = 'make_to_order'

            if record.procure_method.upper() == 'M':
                vals_product['procure_method'] = 'make_to_stock'
            if record.procure_method.upper() == 'B':
                vals_product['procure_method'] = 'make_to_order'

        if hasattr(record, 'cost_method') and record.cost_method:
            if record.cost_method.lower() == 'average price':
                vals_product['cost_method'] = 'average'
            else:
                vals_product['cost_method'] = 'standard'

        if hasattr(record, 'tax_out') and record.tax_out:
            taxes_ids = self.get_taxes(cr, uid, record.tax_out)
            if taxes_ids:
                vals_product['taxes_id'] = [(6, 0, taxes_ids)]
            else:
                error = "Row {0}: Can't find tax for specified Codice Iva".format(self.processed_lines)
                _logger.error(error)
                self.error.append(error)

        if hasattr(record, 'tax_in') and record.tax_in:
            supplier_taxes_ids = self.get_taxes(cr, uid, record.tax_in)
            if supplier_taxes_ids:
                vals_product['supplier_taxes_id'] = [(6, 0, supplier_taxes_ids)]
            else:
                error = "Row {0}: Can't find tax for specified Codice Iva {1}".format(self.processed_lines, record.tax_in)
                _logger.error(error)
                self.error.append(error)

        if hasattr(record, 'list_price') and record.list_price:
            try:
                vals_product['list_price'] = float(record.list_price)
            except Exception as e:
                error = u"Row {0}: Price not valid {1}: {2}".format(self.processed_lines, record.list_price, e)
                _logger.error(error)
                self.warning.append(error)
                vals_product['list_price'] = 0
        else:
            if 'list_price' in self.PRODUCT_WARNINGS:
                warning = u"Row {0}: No list price for product {1}".format(self.processed_lines, vals_product['name'])
                _logger.warning(warning)
                self.warning.append(warning)

        if hasattr(record, 'supplier') and record.supplier:
            if isinstance(record.supplier, unicode):
                supplier = record.supplier
            else:
                supplier = unicode(record.supplier, 'utf-8')
            try:
                partner_ids = self.get_suppliers(cr, uid, supplier)
            except Exception as e:
                error = u"Row {0}: Supplier not valid {1}: {2}".format(self.processed_lines, record.supplier, e)
                _logger.error(error)
                self.warning.append(error)
                partner_ids = False
        else:
            partner_ids = False

        if hasattr(record, 'supplier_product_code') and record.supplier_product_code:
            product_code = record.supplier_product_code
        else:
            product_code = False

        if hasattr(record, 'standard_price') and record.standard_price:
            vals_product['standard_price'] = float(self.toStr(record.standard_price))
        else:
            if 'standard_price' in self.PRODUCT_WARNINGS:
                warning = u"Row {0}: No standard price for product {1}".format(self.processed_lines, vals_product['name'])
                _logger.warning(warning)
                self.warning.append(warning)

        if hasattr(record, 'available_in_pos') and record.available_in_pos:
            if record.available_in_pos.lower() == 'true':
                vals_product['available_in_pos'] = True
            else:
                vals_product['available_in_pos'] = False

        if hasattr(record, 'sale_ok') and record.sale_ok:
            if record.sale_ok.lower() == 'true':
                vals_product['sale_ok'] = True
            else:
                vals_product['sale_ok'] = False

        if hasattr(record, 'ean13') and record.ean13:
            if check_ean(record.ean13):
                vals_product['ean13'] = record.ean13
            else:
                if 'ean13' in self.PRODUCT_ERRORS:
                    error = "Row {0}: '{1}' is not a valid EAN13 code".format(self.processed_lines, vals_product['ean13'])
                    _logger.error(error)
                    self.error.append(error)
                    return False

        if hasattr(record, 'weight_net') and record.weight_net:
            vals_product['weight_net'] = record.weight_net

        if hasattr(record, 'measures') and record.measures:
            vals_product['measures'] = record.measures

        if hasattr(record, 'drop_height') and record.drop_height:
            vals_product['drop_height'] = record.drop_height

        if hasattr(record, 'user_age') and record.user_age:
            vals_product['user_age'] = record.user_age

        if hasattr(record, 'sale_line_warn_msg') and record.sale_line_warn_msg:
            vals_product.update({
                'sale_line_warn': 'warning',
                'sale_line_warn_msg': record.sale_line_warn_msg
            })

        vals_product['listprice_update_date'] = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)

        product_ids = self.product_obj.search(cr, uid, [(field, '=ilike', vals_product[field].replace('\\', '\\\\'))], context=self.context)

        if not product_ids:
            product_ids = self.product_obj.search(
                cr, uid,
                [(field, '=ilike', vals_product[field].replace('\\', '\\\\')), ('active', '=', False)],
                context=self.context
            )

        if not product_ids and vals_product.get('default_code', False):
            product_ids = self.product_obj.search(
                cr, uid,
                [('default_code', '=', vals_product['default_code'].replace('\\', '\\\\').strip())],
                context=self.context
            )

        if product_ids:
            _logger.info(u'Row {row}: Updating product {product}...'.format(row=self.processed_lines, product=vals_product[field]))
            product_id = product_ids[0]
            if self.update_product_name:
                vals_product['name'] = self.product_obj.browse(cr, uid, product_id, self.context).name
            self.product_obj.write(cr, uid, product_id, vals_product, self.context)
            self.updated += 1
        else:
            _logger.info(u'Row {row}: Adding product {product}'.format(row=self.processed_lines, product=vals_product[field]))
            default_vals_product = self.PRODUCT_DEFAULTS.copy()
            if not vals_product.get('uom_id') and default_vals_product.get('uom'):
                vals_product['uom_id'] = self.get_uom(cr, uid, default_vals_product['uom'])
                vals_product['uom_po_id'] = vals_product['uom_id']
                del default_vals_product['uom']
            elif not vals_product.get('uom_id'):
                vals_product['uom_id'] = self.get_uom(cr, uid, 'PCE')
                vals_product['uom_po_id'] = vals_product['uom_id']

            default_vals_product.update(vals_product)
            pprint(default_vals_product)
            product_id = self.product_obj.create(cr, uid, default_vals_product, self.context)
            self.uo_new += 1

        if partner_ids and product_id:
            for partner_id in partner_ids:
                supplierinfo_ids = self.supplierinfo_obj.search(cr, uid, [('product_id', '=', product_id), ('name', '=', partner_id)], context=self.context)
                if supplierinfo_ids:
                    _logger.info(u'{0}: Updating supplier info for product {1}'.format(self.processed_lines, vals_product['name']))
                    self.supplierinfo_obj.write(cr, uid, supplierinfo_ids[0], {
                        'name': partner_id,
                        'product_name': vals_product['name'],
                        'product_id': product_id,
                        'min_qty': 1,
                        'product_code': product_code
                        # 'company_id':
                    }, context=self.context)
                else:
                    _logger.info(u'{0}: Creating supplierinfo for product {1}...'.format(self.processed_lines, vals_product['name']))
                    self.supplierinfo_obj.create(cr, uid, {
                        'name': partner_id,
                        'product_name': vals_product['name'],
                        'product_id': product_id,
                        'min_qty': 1,
                        'product_code': product_code
                        # 'company_id':
                    }, context=self.context)
        else:
            _logger.warning(u'{0}: No supplier for product {1}'.format(self.processed_lines, vals_product['name']))

        if hasattr(record, 'qty_available') and record.qty_available:
            self.set_product_qty(cr, uid, product_id, record.qty_available)

        return product_id

    def getProductTemplateID(self, product_id):
        # Get the product_tempalte ID

        # Retrive the record associated with the product id
        productObject = self.pool['product.product'].browse(self.cr, self.uid, product_id, self.context)

        # Retrive the template id
        product_template_id = productObject.product_tmpl_id.id

        # Return the template id
        return product_template_id
