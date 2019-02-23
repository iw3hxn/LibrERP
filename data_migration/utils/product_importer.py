# -*- coding: utf-8 -*-
# © 2013-2018 Didotech srl (www.didotech.com)

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
        self.partnerinfo_model = self.pool['pricelist.partnerinfo']
        self.partner_model = self.pool['res.partner']

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

        self.default_pricelist = False
        self.default_purchase_pricelist = False

        product_model_id = self.pool['ir.model'].search(cr, uid, [('model', '=', 'product.product')], context=context)
        self.ok_supplier_code = self.pool['ir.model.fields'].search(cr, uid, [('model_id', '=', product_model_id),
                                                                         ('name', '=', 'supplier_code')], context=context)

    def setup(self, import_settings=False, config=False):
        # Recupera il record dal database
        if import_settings:
            self.productImportRecord = import_settings
        else:
            self.filedata_obj = self.pool['product.import']
            self.productImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.productImportID, context=self.context)

        self.file_name = self.productImportRecord.file_name.split('\\')[-1]

        self.update_product_name = self.productImportRecord.update_product_name
        self.update_only = self.productImportRecord.update_only

        # ===================================================
        if not config:
            config = getattr(settings, self.productImportRecord.format)
        self.FORMAT = self.productImportRecord.format
        self.HEADER = config.HEADER_PRODUCT
        self.REQUIRED = config.REQUIRED_PRODUCT
        self.PRODUCT_SEARCH = config.PRODUCT_SEARCH
        self.PRODUCT_WARNINGS = config.PRODUCT_WARNINGS
        self.PRODUCT_ERRORS = config.PRODUCT_ERRORS

        # Default values
        self.PRODUCT_DEFAULTS = config.PRODUCT_DEFAULTS

        if self.FORMAT == 'FormatOmnitron':
            company = self.pool['res.company'].browse(self.cr, self.uid, 1, self.context)
            self.default_pricelist = company.partner_id.property_product_pricelist
            self.default_purchase_pricelist = company.partner_id.property_product_pricelist_purchase

            self.pricelist_version_model = self.pool['product.pricelist.version']
            self.pricelist_item_model = self.pool['product.pricelist.item']

        if not len(self.HEADER) == len(config.COLUMNS_PRODUCT.split(',')):
            pprint(zip(self.HEADER, config.COLUMNS_PRODUCT.split(',')))
            raise orm.except_orm('Error: wrong configuration!', 'The length of columns and headers must be the same')

        self.RecordProduct = namedtuple('RecordProduct', config.COLUMNS_PRODUCT)

    def run(self):
        self.setup()

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
            'kg': 'kg',
            'mm': 'mm'
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
            partner_ids = self.pool['res.partner'].search(cr, uid, [
                '|',
                '|',
                ('property_customer_ref', '=ilike', name),
                ('property_supplier_ref', '=ilike', name),
                ('name', '=ilike', name),
                ('supplier', '=', True)
            ], context=self.context)

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

    def update_pricelist(self, list_type, product_id, partner_id, discount):
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        partner = self.partner_model.browse(self.cr, self.uid, partner_id, self.context)
        product = self.product_obj.browse(self.cr, self.uid, product_id, self.context)

        if list_type == 'purchase':
            list_name = "{partner_name} Purchase Pricelist".format(partner_name=partner.name)
            if partner.property_product_pricelist_purchase.id == self.default_purchase_pricelist.id:
                pricelist_id = self.pool['product.pricelist'].create(self.cr, self.uid, {
                    'name': "{partner_name} Purchase Pricelist".format(partner_name=partner.name),
                    'type': list_type
                }, self.context)

                partner.write({'property_product_pricelist_purchase': pricelist_id})
            else:
                pricelist_id = partner.property_product_pricelist_purchase.id
        else:  # 'sale'
            # list_name = "{partner_name} Pricelist".format(partner_name=partner.name)
            # if partner.property_product_pricelist.id == self.default_pricelist.id:
            #     pricelist_id = self.pool['product.pricelist'].create(self.cr, self.uid, {
            #         'name': "{partner_name} Purchase Pricelist".format(partner_name=partner.name),
            #         'type': list_type
            #     }, self.context)
            #
            #     partner.write({'property_product_pricelist': pricelist_id})
            # else:
            #     pricelist_id = partner.property_product_pricelist.id
            pricelist_id = self.default_pricelist.id
            list_name = self.default_pricelist.name

        version_ids = self.pricelist_version_model.search(self.cr, self.uid, [
            '|',
            ('date_end', '=', False),
            ('date_end', '>', today),
            ('pricelist_id', '=', pricelist_id)
        ])
        if version_ids:
            version_id = version_ids[0]
        else:
            version_id = self.pricelist_version_model.create(self.cr, self.uid, {
                'name': "{name} Version".format(name=list_name),
                'pricelist_id': pricelist_id
            }, self.context)

        pricelist_item_ids = self.pricelist_item_model.search(self.cr, self.uid, [
            ('price_version_id', '=', version_id),
            ('categ_id', '=', product.categ_id.id)
        ], context=self.context)

        if pricelist_item_ids:
            return True
        else:
            if list_type == 'purchase':
                self.pricelist_item_model.create(self.cr, self.uid, {
                    'name': "{name} Line".format(name=list_name),
                    'categ_id': product.categ_id.id,
                    'price_discount': - discount / 100.0,
                    'price_version_id': version_id,
                    'base': -2  # 1 - Public Price, 2 - Cost Price, -2 - Partner section of the product form
                }, self.context)
            else:
                self.pricelist_item_model.create(self.cr, self.uid, {
                    'name': "{name} Line".format(name=list_name),
                    'categ_id': product.categ_id.id,
                    'price_discount': discount - 1,
                    'price_version_id': version_id,
                    'base': 2  # Cost Price
                }, self.context)

    def collect_values(self, cr, uid, record, identifier_field):
        # print '>>>>>>>', record.name
        if not self.update_only:
            vals_product = self.product_obj.default_get(cr, uid, [
                'taxes_id',
                'supplier_taxes_id',
                'property_account_income',
                'property_account_expense'
            ], self.context)
            vals_product[identifier_field] = getattr(record, identifier_field)
        else:
            vals_product = {}

        if vals_product.get('taxes_id'):
            vals_product['taxes_id'] = [(6, 0, vals_product.get('taxes_id'))]
        if vals_product.get('supplier_taxes_id'):
            vals_product['supplier_taxes_id'] = [(6, 0, vals_product.get('supplier_taxes_id'))]

        # Check if there are fields that require special treatment:
        if self.FORMAT == 'FormatOmnitron':
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
            elif record.omnitron_procurement == 'PRODOTTO NON GESTITO A MAGAZZINO':
                vals_product.update({
                    'type': 'service',
                    'procure_method': 'make_to_order'
                })

            if record.omnitron_produce_delay:
                produce_delay = {
                    '3 Day': 3,
                    '7 Days': 7,
                    '20 Days': 20
                }
                vals_product['produce_delay'] = produce_delay[record.omnitron_produce_delay]

            if record.description:
                vals_product.update({
                    'name': record.description.replace('\\', ' / '),
                    'description': record.description,
                })

            if not self.update_only:
                vals_product.update({
                    'old_code': record.old_code,
                    'delivery_cost': record.omnitron_delivery_cost or 0.0,
                    'weight_per_meter': float(record.omnitron_weight_per_meter)
                })
            else:
                if record.omnitron_delivery_cost:
                    vals_product['delivery_cost'] = record.omnitron_delivery_cost
                if record.omnitron_weight_per_meter and float(record.omnitron_weight_per_meter):
                    vals_product['weight_per_meter'] = float(record.omnitron_weight_per_meter)

        elif hasattr(record, 'name'):
            if isinstance(record.name, unicode):
                vals_product['name'] = record.name
            else:
                vals_product['name'] = unicode(record.name, 'utf-8')

        if hasattr(record, 'category') and record.category:
            # We can't use \ in SQL, so we forced to use \\ which became \\\\
            if '\\\\' in record.category:
                categories = record.category.split('\\\\')
            elif '\\' in record.category:
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
        else:
            if self.FORMAT == 'FormatOmnitron':
                if float(record.omnitron_weight_per_meter):
                    vals_product['uom_id'] = self.get_uom(cr, uid, 'm')
                    vals_product['uom_po_id'] = self.get_uom(cr, uid, 'm')

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

        if hasattr(record, 'type') and record.type:
            if record.type.lower() in ['service', 'servizio']:
                vals_product['type'] = 'service'

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
            if record.cost_method.lower() == 'average price' or record.cost_method.lower() == 'average':
                vals_product['cost_method'] = 'average'
            else:
                vals_product['cost_method'] = 'standard'

        if hasattr(record, 'tax_out') and record.tax_out:
            taxes_ids = self.get_taxes(cr, uid, record.tax_out)
            if taxes_ids:
                vals_product['taxes_id'] = [(6, 0, taxes_ids)]
            else:
                error = "Row {0}: Can't find tax for specified Codice Iva {1}".format(self.processed_lines, record.tax_out)
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

        if hasattr(record, 'tax') and record.tax:
            tax = "{:0>2s}".format(record.tax)
            taxes_ids = self.get_taxes(cr, uid, tax + 'v')
            supplier_taxes_ids = self.get_taxes(cr, uid, tax + 'a')

            if taxes_ids:
                vals_product['taxes_id'] = [(6, 0, taxes_ids)]
            else:
                error = "Row {0}: Can't find tax for specified Codice Iva {1}".format(self.processed_lines, record.tax)
                _logger.error(error)
                self.error.append(error)

            if supplier_taxes_ids:
                vals_product['supplier_taxes_id'] = [(6, 0, supplier_taxes_ids)]
            else:
                error = "Row {0}: Can't find tax for specified Codice Iva {1}".format(self.processed_lines, record.tax)
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
            try:
                vals_product['standard_price'] = float(self.toStr(record.standard_price))
            except Exception as e:
                error = u"Row {0}: Price not valid {1}: {2}".format(self.processed_lines, record.standard_price, e)
                _logger.error(error)
                self.warning.append(error)
                vals_product['standard_price'] = 0
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
            real_ean13 = "{:0>13s}".format(record.ean13)
            if check_ean(real_ean13):
                vals_product['ean13'] = real_ean13
            else:
                if 'ean13' in self.PRODUCT_ERRORS:
                    error = "Row {0}: '{1}' is not a valid EAN13 code".format(self.processed_lines, real_ean13)
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

        if not vals_product.get('default_code', False) and vals_product.get('ean13', False):
            vals_product['default_code'] = vals_product['ean13']

        if not self.update_only:
            vals_product['listprice_update_date'] = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)

        return vals_product, product_code, partner_ids

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
                """.format(row=self.processed_lines, row_len=len(row_list), expected=len(self.HEADER),
                           keys=self.HEADER, header=', '.join(map(lambda s: s or '', row_str_list)))

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
        _logger.debug(record)

        identifier_field = self.PRODUCT_SEARCH[0]
        identifier = getattr(record, identifier_field)
        if identifier:
            identifier = identifier.strip()

        for field in self.PRODUCT_SEARCH:
            if hasattr(record, field) and getattr(record, field):
                identifier_field = field
                identifier = getattr(record, identifier_field)
                break
        else:
            error = "Row {0}: Can't find valid product key".format(self.processed_lines)
            _logger.error(error)
            self.error.append(error)
            return False

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

        collected_values = self.collect_values(cr, uid, record, identifier_field)
        if collected_values:
            vals_product, product_code, partner_ids = collected_values

        product_ids = self.product_obj.search(
            cr, uid, [(identifier_field, '=ilike', identifier.replace('\\', '\\\\'))], context=self.context)

        if not product_ids:
            product_ids = self.product_obj.search(
                cr, uid,
                [(identifier_field, '=ilike', identifier.replace('\\', '\\\\')), ('active', '=', False)],
                context=self.context
            )

        if not product_ids and vals_product.get('default_code', False):
            product_ids = self.product_obj.search(
                cr, uid,
                [('default_code', '=', vals_product['default_code'].replace('\\', '\\\\').strip())],
                context=self.context
            )
        if not product_ids and product_code:
            if self.ok_supplier_code:
                product_ids = self.product_obj.search(cr, uid, [('supplier_code', '=', product_code)], context=self.context)

        if not product_ids and self.FORMAT == 'FormatStandardPriceUpdate':
            product_ids = self.product_obj.search(cr, uid, [('supplier_code', '=', identifier)], context=self.context)

        if product_ids:
            product_id = product_ids[0]
            if not self.update_product_name and 'name' in vals_product:
                # vals_product['name'] = self.product_obj.browse(cr, uid, product_id, self.context).name
                name = vals_product['name']
                del vals_product['name']
            else:
                name = 'Unknown'

            if vals_product:
                _logger.info(
                    u'Row {row}: Updating product {product}...'.format(row=self.processed_lines, product=identifier))
                self.product_obj.write(cr, uid, product_id, vals_product, self.context)

            if 'name' not in vals_product:
                vals_product['name'] = name
            self.updated += 1
        elif not self.update_only:
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
        else:
            product_id = False

        if partner_ids and product_id:
            if hasattr(record, 'description_english') and record.description_english:
                self.product_obj.write(
                    cr, uid, product_id, {'description': record.description_english}, context={'lang': 'en_US'}
                )

            for partner_id in partner_ids:
                supplierinfo_ids = self.supplierinfo_obj.search(cr, uid, [
                    ('product_id', '=', product_id),
                    ('name', '=', partner_id)
                ], context=self.context)

                suppinfo_vals = {
                    'name': partner_id,
                    'product_name': vals_product['name'],
                    'product_id': product_id,
                    'min_qty': 1,
                    'product_code': product_code,
                }
                if hasattr(record, 'supplier_price') and record.supplier_price or hasattr(record,
                                                                                          'standard_price') and record.standard_price:
                    price = hasattr(record, 'supplier_price') and record.supplier_price or hasattr(record,
                                                                                                   'standard_price') and record.standard_price or 0.0
                    if 'weight_per_meter' in vals_product:
                        price = float(price) / vals_product.get('weight_per_meter', 1)

                    suppinfo_vals['pricelist_ids'] = [
                        (0, False, {'min_quantity': 1, 'price': price})
                    ]

                if supplierinfo_ids:
                    _logger.info(u'{0}: Updating supplier info for product {1}'.format(
                        self.processed_lines, vals_product['name']
                    ))
                    suppinfo_id = supplierinfo_ids[0]

                    if 'pricelist_ids' in suppinfo_vals:
                        supplierinfo = self.supplierinfo_obj.browse(cr, uid, suppinfo_id, context=self.context)
                        if supplierinfo.pricelist_ids:
                            remove_ids = [(2, pricelist.id) for pricelist in supplierinfo.pricelist_ids]
                            suppinfo_vals['pricelist_ids'] = remove_ids + suppinfo_vals['pricelist_ids']

                    self.supplierinfo_obj.write(cr, uid, suppinfo_id, suppinfo_vals, context=self.context)
                else:
                    _logger.info(u'{0}: Creating supplierinfo for product {1}...'.format(
                        self.processed_lines, vals_product['name'])
                    )
                    suppinfo_id = self.supplierinfo_obj.create(cr, uid, suppinfo_vals, context=self.context)

                # if hasattr(record, 'supplier_price') and record.supplier_price:
                #     partnerinfo_ids = self.partnerinfo_model.search(cr, uid, [
                #         ('suppinfo_id', '=', suppinfo_id),
                #         ('min_quantity', '=', 1)
                #     ], context=self.context)

                    # if partnerinfo_ids:
                    #     self.partnerinfo_model.write(cr, uid, partnerinfo_ids[0], {'price': record.supplier_price})
                    # else:
                    #     self.partnerinfo_model.create(cr, uid, {
                    #         'price': record.supplier_price,
                    #         'suppinfo_id': suppinfo_id,
                    #         'min_quantity': 1
                    #     })

                if vals_product.get('categ_id', False) and hasattr(record, 'discount') and record.discount:
                    self.update_pricelist('purchase', product_id, partner_id, float(record.discount))
                # if vals_product.get('categ_id', False) and hasattr(record, 'k_sale_price') and record.k_sale_price:
                #     self.update_pricelist('sale', product_id, partner_id, float(record.k_sale_price))

        else:
            _logger.warning(
                u'{0}: No supplier for product {1}'.format(
                    self.processed_lines,
                    vals_product.get('name') or vals_product.get('description')))

        if product_id and hasattr(record, 'qty_available') and record.qty_available:
            self.set_product_qty(cr, uid, product_id, record.qty_available)

        if self.update_only:
            return True
        else:
            return product_id

    def getProductTemplateID(self, product_id):
        # Get the product_tempalte ID

        # Retrive the record associated with the product id
        productObject = self.pool['product.product'].browse(self.cr, self.uid, product_id, self.context)

        # Retrive the template id
        product_template_id = productObject.product_tmpl_id.id

        # Return the template id
        return product_template_id
