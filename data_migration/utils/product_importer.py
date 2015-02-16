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

import pooler
import threading
from tools.translate import _
from openerp.osv import orm
import math
from product.product import check_ean
import data_migration.settings as settings
from collections import namedtuple
from pprint import pprint
from utils import Utils
from openerp.addons.core_extended.file_manipulation import import_sheet

import logging
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
    
    def run(self):
        # Recupera il record dal database
        self.filedata_obj = self.pool.get('product.import')
        self.productImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.productImportID, context=self.context)
        self.file_name = self.productImportRecord.file_name.split('\\')[-1]

        self.update_product_name = self.productImportRecord.update_product_name
        
        # ===================================================
        Config = getattr(settings, self.productImportRecord.format)

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

        table, self.numberOfLines = import_sheet(self.file_name, self.productImportRecord.content_text)

        if DEBUG:
            # Importa il listino
            self.process(self.cr, self.uid, table)
            
            # Genera il report sull'importazione
            self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata')
        else:
            # Elaborazione del listino prezzi
            try:
                # Importa il listino
                self.process(self.cr, self.uid, table)
                
                # Genera il report sull'importazione
                self.notify_import_result(self.cr, self.uid, self.message_title, 'Importazione completata')
            except Exception as e:
                # Annulla le modifiche fatte
                self.cr.rollback()
                self.cr.commit()
                
                title = "Import failed"
                message = "Errore alla linea %s" % self.processed_lines + "\nDettaglio:\n\n" + str(e)
                
                if DEBUG:
                    ### Debug
                    _logger.debug(message)
                    pdb.set_trace()
                
                self.notify_import_result(self.cr, self.uid, title, message, error=True)

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
        if categories:
            if DEBUG:
                print(categories)
            category_obj = self.pool['product.category']
            name = categories.pop(0)
            category_ids = category_obj.search(cr, uid, [('name', '=', name.strip()), ('parent_id', '=', parent_id)])

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
                #error = "Row {0}: Category '{1}' is missing in database".format(self.processed_lines, name)
                #_logger.error(error)
                #self.error.append(error)
                #return False

                category_id = category_obj.create(cr, uid, {'name': name, 'parent_id': parent_id})
                
                if categories:
                    return self.get_category(cr, uid, categories, category_id)
                else:
                    return category_id
                
        return False
            
    def get_uom(self, cr, uid, name):
        translate = {
            'kgm': 'kg',
            'unit': 'Unit(s)',
            'litre': 'Liter(s)',
            'PCE': 'PCE'
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
        
        uom_ids = self.pool.get('product.uom').search(cr, uid, [('name', '=ilike', translate[uom_name])])
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
        tax_obj = self.pool.get('account.tax')
        
        tax_ids = tax_obj.search(cr, uid, [('description', '=', description)])
        
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
            partner_ids = self.pool['res.partner'].search(cr, uid, [('name', '=ilike', name), ('supplier', '=', True)])
            
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
        brand_ids = brand_obj.search(cr, uid, [('name', '=ilike', name)])
        
        if len(brand_ids) == 1:
            return brand_ids[0]
        elif len(brand_ids) > 1:
            warning = "Row {0}: Abnormal situation. More than one brand '{1}' found".format(self.processed_lines, name)
            _logger.warning(warning)
            self.warning.append(warning)
            return False
        else:
            return brand_obj.create(cr, uid, {'name': name})
    
    def import_row(self, cr, uid, row_list):
        if self.first_row:
            row_str_list = [self.toStr(value) for value in row_list]
            for column in row_str_list:
                #print column
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
                """.format(row=self.processed_lines, row_len=len(row_list), expected=len(self.HEADER), keys=self.HEADER, header=', '.join(row_str_list))

            _logger.error(str(row_list))
            _logger.error(error)
            self.error.append(error)
            return False
        elif DEBUG:
            #pprint(row_list)
            row_str_list = [self.toStr(value) for value in row_list]
            pprint(zip(self.HEADER, row_str_list))
        
        # Sometime value is only numeric and we don't want string to be treated as Float
        record = self.RecordProduct._make([self.toStr(value) for value in row_list])
        
        for field in self.REQUIRED:
            if not getattr(record, field):
                error = "Riga {0}: Manca il valore della {1}. La riga viene ignorata.".format(self.processed_lines, field)
                _logger.debug(error)
                self.error.append(error)
                return False
        
        vals_product = self.PRODUCT_DEFAULTS.copy()
        
        vals_product['name'] = record.name
        
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
            categories = record.category.split('\\')
            vals_product['categ_id'] = self.get_category(cr, uid, categories)

        if hasattr(record, 'brand') and record.brand:
            vals_product['product_brand_id'] = self.get_brand(cr, uid, record.brand)
        
        if hasattr(record, 'description_sale') and record.description_sale:
            vals_product['description_sale'] = record.description_sale
        
        if hasattr(record, 'uom') and record.uom:
            vals_product['uom_id'] = self.get_uom(cr, uid, record.uom)
            vals_product['uom_po_id'] = vals_product['uom_id']
        elif vals_product.get('uom', False):
            vals_product['uom_id'] = self.get_uom(cr, uid, vals_product['uom'])
            vals_product['uom_po_id'] = vals_product['uom_id']
            del vals_product['uom']

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
            vals_product['list_price'] = float(record.list_price)
        else:
            if 'list_price' in self.PRODUCT_WARNINGS:
                warning = u"Row {0}: No list price for product {1}".format(self.processed_lines, vals_product['name'])
                _logger.warning(warning)
                self.warning.append(warning)
        
        if hasattr(record, 'supplier') and record.supplier:
            partner_ids = self.get_suppliers(cr, uid, record.supplier)
        else:
            partner_ids = False
        
        if hasattr(record, 'supplier_product_code') and record.supplier_product_code:
            product_code = record.supplier_product_code
        else:
            product_code = False
                    
        if hasattr(record, 'standard_price') and record.standard_price:
            vals_product['standard_price'] = float(record.standard_price)
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

        product_ids = self.product_obj.search(cr, uid, [(field, '=ilike', vals_product[field].replace('\\', '\\\\'))])
        if product_ids:
            _logger.info(u'Row {row}: Updating product {product}...'.format(row=self.processed_lines, product=vals_product[field]))
            product_id = product_ids[0]
            if self.update_product_name:
                vals_product['name'] = self.product_obj.browse(cr, uid, product_id, context=None).name
            self.product_obj.write(cr, uid, product_id, vals_product)
            self.updated += 1
        else:
            _logger.info(u'Row {row}: Adding product {product}...'.format(row=self.processed_lines, product=vals_product[field]))
            #print(vals)
            # Create new product
            product_id = self.product_obj.create(cr, uid, vals_product)
            self.uo_new += 1
        
        if partner_ids and product_id:
            for partner_id in partner_ids:
                supplierinfo_ids = self.supplierinfo_obj.search(cr, uid, [('product_id', '=', product_id), ('name', '=', partner_id)])
                if supplierinfo_ids:
                    _logger.info(u'{0}: Updating supplierinfo for product {1}'.format(self.processed_lines, vals_product['name']))
                    self.supplierinfo_obj.write(cr, uid, supplierinfo_ids[0], {
                        'name': partner_id,
                        'product_name': vals_product['name'],
                        'product_id': product_id,
                        'min_qty': 1,
                        'product_code': product_code
                        #'company_id':
                    })
                else:
                    _logger.info(u'{0}: Creating supplierinfo for product {1}...'.format(self.processed_lines, vals_product['name']))
                    self.supplierinfo_obj.create(cr, uid, {
                        'name': partner_id,
                        'product_name': vals_product['name'],
                        'product_id': product_id,
                        'min_qty': 1,
                        'product_code': product_code
                        #'company_id':
                    })
        else:
            _logger.warning(u'{0}: No supplier for product {1}'.format(self.processed_lines, vals_product['name']))
        
        return product_id
            
    def getProductTemplateID(self, product_id):
        # Get the product_tempalte ID
        
        # Retrive the record associated with the product id
        productObject = self.pool.get('product.product').browse(self.cr, self.uid, product_id)
        
        # Retrive the template id
        product_template_id = productObject.product_tmpl_id.id
        
        # Return the template id
        return product_template_id
