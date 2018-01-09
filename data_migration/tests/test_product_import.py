# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

"""
$ workon OE_61
$ export PYTHONPATH=/Users/andrei/Programming/lp/OpenERP_6.1/server_61/:/Users/andrei/Programming/lp/openerp-command/
$ export PATH=/Users/andrei/Programming/lp/OpenERP_6.1/server_61/:/Users/andrei/Programming/lp/openerp-command/:$PATH
$ oe run-tests -m data_migration -d <database_name> --addons /Users/andrei/Programming/lp/OpenERP_6.1/aeroo/:/Users/andrei/Programming/lp/LibrERP/:/Users/andrei/Programming/lp/OpenERP_6.1/addons_61

"""

from openerp.tests.common import TransactionCase
from openerp.addons.data_migration.utils.product_importer import ImportFile
import unittest2


class TestFormat3ProductImport(TransactionCase):
    class ImportConfig(object):
        DEBUG = True
        HEADER_PRODUCT = (
            'Codice', 'Nome', 'Categoria', 'UoM', 'codiva_acq', 'codiva_cen',
            'list_price', 'EAN13', 'fornitore', 'cod__prod__forn_', 'prezzo_forn_',
            'active', 'available_in_pos', 'sale_ok', 'assupply_method', 'type',
            'procure_method', 'cost_method'
        )

        COLUMNS_PRODUCT = "default_code, name, category, uom, tax_in, tax_out," \
                          "list_price, ean13, supplier, supplier_product_code, " \
                          "standard_price, active, null, sale_ok, " \
                          "supply_method, type, procure_method, cost_method"
        PRODUCT_SEARCH = ('default_code', 'name')
        REQUIRED_PRODUCT = ['name']
        PRODUCT_WARNINGS = []
        PRODUCT_ERRORS = []

        # Default values
        PRODUCT_DEFAULTS = {
            'supply_method': 'buy',
            'uom': 'PCE',
            # 'type': 'consu',
            'type': 'product',
            'procure_method': 'make_to_stock',
            'cost_method': 'standard',
            'sale_ok': True
        }

    class ImportSettings(object):
        state = 'end'

        # Data of file, in code BASE64
        content_base64 = False
        file_name = 'Format3'
        format = 'FormatThree'
        progress_indicator = 0
        # strict = False
        # partner_type = 'customer'
        update_only = False
        update_product_name = False
        # _model = 'product.product'

    def setUp(self):
        super(TestFormat3ProductImport, self).setUp()
        self.import_model = ImportFile(self.cr, self.uid, [False], context={})
        self.import_model.setup(self.ImportSettings, self.ImportConfig)
        self.import_model.processed_lines = 0

    def test_import(self):
        test_values = [
            {
                'request': [
                    False, "Dos P016 - 1C / 01", "Products / Dispensing / Scheugenpflug / DosP",
                    1, False, False, False, False, "Scheugenpflug", "VA10001", "6,200.00", "y",
                    False, False, False, False, False, False
                ],
                'identifier_field': 'name',
                'reply': {
                    'uom_po_id': 1, 'name': u'Dos P016 - 1C / 01', 'listprice_update_date': '2018-01-08',
                    'property_account_expense': False, 'standard_price': 6200.0,
                    u'supplier_taxes_id': [(6, 0, [1L])], 'uom_id': 1, u'taxes_id': [(6, 0, [2L])],
                    'property_account_income': False, 'categ_id': 673L
                }
            },
            {
                'request': [
                    False, "Barrel Follower Plate Pump( for Small Barrels)",
                    "Products / Dispensing / Scheugenpflug / A90",
                    1, False, False, False, False,
                    "Scheugenpflug", "VA10062", "auf Anfrage / upon request", "y",
                    False, False, False, False, False, False
                ],
                'identifier_field': 'name',
                'reply': {
                    'standard_price': False
                }
            }

        ]

        for values in test_values:
            record = self.import_model.RecordProduct._make([self.import_model.toStr(value) for value in values['request']])
            print record

            vals_product, product_code, partner_ids = self.import_model.collect_values(
                self.cr, self.uid, record, values['identifier_field'])
            print vals_product
            self.assertEqual(values['reply']['standard_price'], vals_product['standard_price'], 'Wrong price')


if __name__ == '__main__':
    unittest2.main()
