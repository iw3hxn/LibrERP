# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2016 Didotech srl (info at didotech.com)
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

# DEBUG = True
DEBUG = False

from collections import OrderedDict


class FormatOne():
    # R.
    HEADER_CUSTOMER = (
        u'Codice', u'Ragione Sociale', u'Nome', u'Indirizzo',
        u'CAP', u'Località', u'Provincia', u'Indirizzo AM',
        u'CAP AM', u'Località AM', u'Provincia AM', u'Nazione',
        u'Partita IVA', u'Codice Fiscale', u'E-Mail', u'Category'
    )
    COLUMNS = "code, name, person_name, street_default, zip_default, "\
              "city_default, province_default, street_invoice, zip_invoice, "\
              "city_invoice, province_invoice, country_code, vat, fiscalcode, "\
              "email, category"
    REQUIRED = ['name', 'code']
    ADDRESS_TYPE = ('default', 'invoice',)
    # Unique fields to be used to look for partner in database
    PARTNER_SEARCH = ('name', 'vat')

    HEADER_PRODUCT = (
        'Codice', 'Descrizione', 'UMC', 'UMT',
        'PesoN', 'CostoStd', 'CostoUltimo'
    )
    COLUMNS_PRODUCT = "default_code, name, uom, uom2, weight_net, "\
                      "standard_price, last_standard_price"
    PRODUCT_SEARCH = ['default_code', 'name']
    REQUIRED_PRODUCT = ['default_code', 'name']
    PRODUCT_WARNINGS = ['standard_price']
    PRODUCT_ERRORS = []

    # Default values
    PRODUCT_DEFAULTS = {
        'supply_method': 'buy',
        'uom_id': 'PCE',
        # 'type': 'consu',
        'type': 'product',
        'procure_method': 'make_to_stock',
        'cost_method': 'standard',
    }

    HEADER_CRM = (
        'CLIENTE', 'PIVA', 'INDIRIZZO', 'COMUNE', 'TELEFONO', 'REFERENTE', 'KO IMMEDIATO (RIFIUTO APPUNTAMENTO) + MOTIVAZIONI'
    )
    COLUMNS_CRM = ['partner_name', 'vat', 'street', 'city', 'phone', 'contact_name', 'description']
    CRM_SEARCH = ['partner_name']
    REQUIRED_CRM = ['partner_name', 'vat']
    CRM_WARNINGS = []
    CRM_ERRORS = []

    # Default values
    CRM_DEFAULTS = {
    }

    HEADER_PICKING = (
        'RtbTipdoc', 'RtbNumbol', 'RtbDatbol',
        'RboCodart', 'RboUnimis', 'RboQuanti'
    )
    COLUMNS_PICKING = "doc, origin, date, product, product_uom, qty"
    REQUIRED_PICKING = ['origin', 'date',
        'product', 'product_uom', 'qty'
    ]

    HEADER_PRICELIST_ITEM = ('Articolo', 'Prezzo')
    COLUMNS_PRICELIST_ITEM = "code, price_surcharge"
    REQUIRED_PRICELIST_ITEM = ['code', 'price_surcharge']

    HEADER_SALES_ITEM = ('Location', 'Location Name', 'SKU', 'Item Style', 'SKU Description', 'Transaction Date', 'Quantity', 'Extended Cost', 'Item Ledg. Entry No.', 'Gen. Business Posting Group')
    COLUMNS_SALES_ITEM = "location, location_name, sku, item, sku_description, date, qty, cost, item2, group"
    REQUIRED_SALES_ITEM = ['item', 'qty']

    HEADER_INVOICE_ITEM = ('Location', 'Location Name', 'SKU', 'Item Style', 'SKU Description', 'Transaction Date', 'Quantity', 'Extended Cost', 'Item Ledg. Entry No.', 'Gen. Business Posting Group')
    COLUMNS_INVOICE_ITEM = "location, location_name, sku, item, sku_description, date, qty, cost, item2, group"
    REQUIRED_INVOICE_ITEM = ['item', 'qty']

    HEADER_INVENTORY_ITEM = ('Articolo', 'Quantità')
    COLUMNS_INVENTORY_ITEM = "default_code, product_qty"
    REQUIRED_INVENTORY_ITEM = ['default_code']
    INVENTORY_PRODUCT_SEARCH = ['default_code']


class FormatTwo():
    # IB.
    HEADER_CUSTOMER = (
        u'Codice', u'Denominazione / Cognome', u'Nome',
        u'Sede legale: indirizzo', u'SL: CAP', u'SL: località',
        u'SL: Prov.', u'Telefono', u'Fax',
        u'e-mail', u'Sede amministrativa: indirizzo 1',
        u'Sede amministrativa: indirizzo 2', u'SA: CAP', u'SA: località',
        u'SA: Prov.', u'Nazione', u'PI', u'CF', u'category', u'Note'
    )
    # COLUMNS = "code, name, person_name, street_default, zip_default, "\
    #           "city_default, province_default, phone_default, "\
    #           "fax_default, email_default, street_invoice, "\
    #           "street2_invoice, zip_invoice, city_invoice, "\
    #           "province_invoice, country_code, vat, "\
    #           "fiscalcode, category, comment"
    COLUMNS = "code, name, person_name, street_invoice, zip_invoice, "\
              "city_invoice, province_invoice, phone_invoice, fax_invoice, "\
              "email_invoice, street_delivery, street2_delivery, "\
              "zip_delivery, city_delivery, province_delivery, country_code, "\
              "vat, fiscalcode, category, comment"
    REQUIRED = ('name', 'code')
    ADDRESS_TYPE = ('invoice', 'delivery')
    # Unique fields to be used to look for partner in database
    PARTNER_SEARCH = ['name', 'vat']

    # HEADER_PRODUCT = (
    #     'Codice', 'Descrizione', 'UMC', 'UMT', 'PesoN',
    #     'CostoStd', 'CostoUltimo'
    # )
    # COLUMNS_PRODUCT = "default_code, name, uom0, uom2, weight_net, "\
    #                   "standard_price, last_standard_price"
    # PRODUCT_SEARCH = ('default_code', 'name')
    # REQUIRED_PRODUCT = ['default_code', 'name']
    # PRODUCT_WARNINGS = ['standard_price']
    # PRODUCT_ERRORS = []

    HEADER_PICKING = (
        'NAME', 'DATE', 'STYLE NUMBER', 'QUANTITY'
    )
    COLUMNS_PICKING = "origin, date, product, qty"
    REQUIRED_PICKING = [
        'origin', 'date', 'product', 'qty'
    ]

    HEADER_INVOICE_ITEM = ('Number', 'Date', 'Customer Name', 'Total Amount')
    COLUMNS_INVOICE_ITEM = "number_invoice, date_invoice, partner_name, total_amount"
    REQUIRED_INVOICE_ITEM = ['number_invoice', 'date_invoice', 'partner_name']

    HEADER_INVENTORY_ITEM = ('Articolo', 'Quantità', 'Seriale / Lotto', 'Prezzo', 'Locazione')
    COLUMNS_INVENTORY_ITEM = "default_code, product_qty, prod_lot, price, location"
    REQUIRED_INVENTORY_ITEM = ['default_code']
    INVENTORY_PRODUCT_SEARCH = ['default_code']


class FormatThree():
    # TP
    HEADER_CUSTOMER = (
        u'Codice', u'Denominazione / Cognome', u'Nome',
        u'Sede legale: indirizzo', u'SL: CAP', u'SL: località', u'SL: Prov.',
        u'Telefono', u'Fax', u'e-mail', u'Sede amministrativa: indirizzo 1',
        u'Sede amministrativa: indirizzo 2', u'SA: CAP', u'SA: località',
        u'SA: Prov.', u'Nazione', u'PI', u'CF', u'category',
        u'Fiscal Position', u'Payment Term'
    )

    COLUMNS = "code, name, person_name, street_default, zip_default, "\
              "city_default, province_default, phone_default, fax_default, "\
              "email_default, street_invoice, street2_invoice, zip_invoice, "\
              "city_invoice, province_invoice, country_code, vat, "\
              "fiscalcode, category, fiscal_position, payment_term"

    REQUIRED = ('name', 'code')
    ADDRESS_TYPE = ('default', 'invoice',)
    # Unique fields to be used to look for partner in database
    PARTNER_SEARCH = ['name', 'vat']

    HEADER_PRODUCT = (
        'Codice', 'Nome', 'Categoria', 'UoM', 'codiva_acq', 'codiva_cen',
        'list_price', 'EAN13', 'fornitore', 'cod__prod__forn_', 'prezzo_forn_',
        'active', 'available_in_pos', 'sale_ok', 'assupply_method', 'type',
        'procure_method', 'cost_method'
    )

    COLUMNS_PRODUCT = "default_code, name, category, uom, tax_in, tax_out,"\
                      "list_price, ean13, supplier, supplier_product_code, "\
                      "standard_price, active, null, sale_ok, "\
                      "supply_method, type, procure_method, cost_method"
    PRODUCT_SEARCH = ('default_code', 'name')
    REQUIRED_PRODUCT = ['default_code', 'name']
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

    HEADER_INVENTORY_ITEM = ('Articolo', 'Quantità', 'Prezzo')
    COLUMNS_INVENTORY_ITEM = "default_code, product_qty, average_cost"
    REQUIRED_INVENTORY_ITEM = ['default_code']
    INVENTORY_PRODUCT_SEARCH = ['default_code']


class FormatFour():
    # TP Extended (differs only for product import)
    HEADER_CUSTOMER = (
        u'Codice', u'Denominazione / Cognome', u'Nome',
        u'Sede legale: indirizzo', u'SL: CAP', u'SL: località', u'SL: Prov.',
        u'Telefono', u'Fax', u'e-mail', u'Sede amministrativa: indirizzo 1',
        u'Sede amministrativa: indirizzo 2', u'SA: CAP', u'SA: località',
        u'SA: Prov.', u'Nazione', u'PI', u'CF', u'category'
    )

    COLUMNS = "code, name, person_name, street_default, zip_default, "\
              "city_default, province_default, phone_default, fax_default, "\
              "email_default, street_invoice, street2_invoice, zip_invoice, "\
              "city_invoice, province_invoice, country_code, vat, "\
              "fiscalcode, category"
    # COLUMNS = "code, name, person_name, street_invoice, zip_invoice, "\
    #           "city_invoice, province_invoice, phone_invoice, fax_invoice, "\
    #           "email_invoice, street_delivery, street2_delivery, "\
    #           "zip_delivery, city_delivery, province_delivery, "\
    #           "country_code, vat, fiscalcode, email2, category"

    REQUIRED = ('name', )
    ADDRESS_TYPE = ('default', 'invoice',)
    # Unique fields to be used to look for partner in database
    PARTNER_SEARCH = ['vat', 'name']

    HEADER_PRODUCT = (
        'codice', 'nome', 'categoria', 'brand', 'descrizione vendita', 'uom_i',
        'codiva_acq', 'codiva_cen', 'list_price', 'ean13', 'fornitore',
        'cod__prod__forn_', 'prezzo_forn_', 'active', 'available_in_pos',
        'sale_ok', 'assupply_method', 'type', 'procure_method', 'cost_method'
    )
    COLUMNS_PRODUCT = "default_code, name, category, brand, "\
                      "description_sale, uom, tax_in, tax_out, list_price, "\
                      "ean13, supplier, supplier_product_code, "\
                      "standard_price, active, null, sale_ok, "\
                      "supply_method, type, procure_method, cost_method"
    PRODUCT_SEARCH = ('default_code', 'name')
    REQUIRED_PRODUCT = ['default_code', 'name']
    PRODUCT_WARNINGS = []
    PRODUCT_ERRORS = []

    # Default values
    PRODUCT_DEFAULTS = {
        'supply_method': 'buy',
        'uom': 'PCE',
        # 'type': 'consu',
        'type': 'product',
        'procure_method': 'make_to_order',
        'cost_method': 'standard',
        'sale_ok': True
    }


class FormatFive():
    # TP Extended (differs only for product import)
    HEADER_CUSTOMER = (
        u'#', u'Codice BP', u'Nome BP', u'Via (destinatario consegna)', u'CAP (destinatario consegna)',
        u'Località (destinatario fattura)', u'Stato federato (destinatario consegna)', u'Telefono 1', u'Numero di fax',
        u'E-mail', u'Via (destinatario fattura)', u'CAP (destinatario fattura)', u'Località (destinatario fattura)',
        u'Stato federato (destinatario fattura)', u'Partita IVA', u'Partita IVA', u'Partita IVA unica',
        u'N. ID supplementare', u'Tipo di gruppo', u'Area', u'Soggetto tratt. fonte', u'Codice ritenuta d\'acconto',
        u'Gruppo trattenute ritenuta d\'acconto', u'Gruppo d\'imposta', u'Nome gruppo per cond. di pag.', u'Limite fido'
    )
    COLUMNS = "index, code, name, street_default, zip_default, "\
              "city_default, province_default, phone_default, fax_default, "\
              "email_default, street_invoice, zip_invoice, city_invoice, "\
              "province_invoice, vat, vat2, fiscalcode, "\
              "additional_id, group_type, area, sbj_retention_source, down_payment_code, "\
              "down_payment_group, tax_group, payment_term, credit_limit"
    REQUIRED = ('name',)
    ADDRESS_TYPE = ('default', 'invoice',)
    # Unique fields to be used to look for partner in database
    PARTNER_SEARCH = ['code', 'vat', 'name']

    HEADER_PRODUCT = (
        "pruduct_id", "product_name", "product_description", "product_price",
        "price_min", "product_position", "payment_periodicity", "category_path",
        "category_name", "category_description", "pricelist_id", "pricelist_name",
        "supplier_name", "supplier_vat_number", "product_type_code",
        "product_type_short_description", "product_type_description"
    )

    COLUMNS_PRODUCT = "default_code, name, description_sale, list_price, "\
                      "none, order, order_duration, category, none0, "\
                      "none1, none2, none3, "\
                      "brand, none4, none5, none6, none7"

    PRODUCT_SEARCH = ['default_code', 'name']
    REQUIRED_PRODUCT = ['default_code', 'name']
    PRODUCT_WARNINGS = []
    PRODUCT_ERRORS = []

    # Default values
    PRODUCT_DEFAULTS = {
        'supply_method': 'buy',
        'uom': 'PCE',
        'type': 'service',
        'procure_method': 'make_to_order',
        'cost_method': 'standard',
        'sale_ok': True
    }


class Inventory(object):
    TABLE = OrderedDict((
        ('default_code', 'Product Code'),
        ('name', 'Product Name'),
        ('qty_available', 'Product quantity')
    ))

# Nothing should be changed after this line
# -----------------------------------------------------------------------------

COUNTRY_CODES = {
    'Italia': 'IT',
    'CVA': 'IT',
    '20': 'IT',
    '22': 'CZ',
    'SPA': 'ES',
    'UH': 'HU',
    'Portogallo': 'PT',
    'UK': 'GB',
}
