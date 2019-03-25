# -*- coding: utf-8 -*-
# © 2013 - 2018 Didotech srl (www.didotech.com)

DEBUG = True
# DEBUG = False

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
    PARTNER_UNIQUE_OFFICE_CODE = False

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

    HEADER_BOM = (
        'Articolo superiore', 'Numero dell elemento subordinato', 'Articolo subordinato', 'Quantità', 'Magazzino',
        'Prezzo', 'Divisa', 'Listino prezzi', 'Prezzo nuovo', 'Divisa originale', 'Modalità prelievo',
        'Unità di misura magazzino', 'Osservazione', 'Istanza registro', 'Oggetto', 'Descrizione articolo subordinato',
        'Misure articolo subordinato', 'Regola di distribuzione 3', 'Regola di distribuzione 4',
        'Regola di distribuzione 5', 'Input principale', 'Codice progetto', 'Misure', 'Codice alternativo',
        'Dimensione', 'Materiale'
    )

    COLUMNS_BOM = "default_code, sub_elem_number, sub_item, product_qty, wharehouse, " \
                  "price, divisa, listino_prezzi, prezzo_nuovo, divisa_originale, modalita_prelievo, " \
                  "uom_maga, observation, ist_reg, object, sub_description, " \
                  "sub_dimension, rdd3, rdd4, " \
                  "rdd5, input_principale, codice_progetto, measures, codice_alternativo, " \
                  "dimension, materials"

    # BOM_SEARCH = ['sub_item']
    # Corrected by Andrei:
    BOM_BASE_PRODUCT_SEARCH = ['default_code']
    BOM_SEARCH = ['default_code']
    REQUIRED_BOM = ['sub_item']
    # BOM_WARNINGS = ['standard_price']
    # BOM_ERRORS = []
    # Default values
    BOM_DEFAULTS = {
    }


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
    PARTNER_UNIQUE_OFFICE_CODE = False

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

    # HEADER_PRODUCT = (
    #     'Codice articolo', 'Descrizione articolo', 'Gruppo articoli', 'Descrizione articolo',
    #     'Descrizione in lingua straniera', 'Unità di misura acquisto', 'Definizione IVA acquisti',
    #     'Codice IVA (fornitori)', 'Codice a barre', 'Nome BP', 'Ultimo prezzo d\'acquisto', 'Attivo',
    #     'Metodo di approvvigionamento'
    # )

    HEADER_PRODUCT = (
        'COD.', 'DESCR.1', 'Descrizione Commerciale', 'descrizione inglese', 'misure',
        'Altezza di caduta', 'età utente', 'Unità di misura acquisto', 'categoria', 'Prezzo Vendita',
        'Attivo', 'Metodo di approvvigionamento'
    )
    COLUMNS_PRODUCT = "default_code, name, description_sale, eng_description_sale, measures, " \
                      "drop_height, user_age, uom, category, list_price, " \
                      "active, procure_method"
    PRODUCT_SEARCH = ('default_code', 'name')
    REQUIRED_PRODUCT = ['default_code', 'name']
    PRODUCT_WARNINGS = []
    PRODUCT_ERRORS = []
    # Default values
    PRODUCT_DEFAULTS = {
        'supply_method': 'buy',
        # 'uom': 'PCE',
        # 'type': 'consu',
        'type': 'product',
        'procure_method': 'make_to_order',
        'cost_method': 'standard',
        'sale_ok': True,
    }

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

    HEADER_BOM = (
        'Articolo superiore', 'Descrizione Articolo superiore', 'Numero dell\'elemento subordinato',
        'Articolo subordinato', 'Quantità', 'Articolo superiore', 'Numero dell\'elemento subordinato',
        'Articolo subordinato', 'Quantità', 'Magazzino', 'Prezzo', 'Divisa', 'Listino prezzi', 'Prezzo nuovo',
        'Divisa originale', 'Modalità prelievo', 'Unità di misura magazzino', 'Osservazione', 'Istanza registro',
        'Oggetto', 'Descrizione Articolo Subordinato', 'Misure articolo Subordinato', 'Regola di distribuzione 3',
        'Regola di distribuzione 4', 'Regola di distribuzione 5', 'Input principale', 'Codice progetto', 'Misure',
        'Codice alternativo', 'Dimensione', 'Materiale'
    )
    COLUMNS_BOM = "default_code, name, sub_elem_number, " \
                  "sub_item, product_qty, default_code2, sub_elem_number2, " \
                  "sub_item2, product_qty2, wharehouse, standard_price, divisa, listino_prezzi, prezzo_nuovo, " \
                  "divisa_originale, modalita_prelievo, uom_maga, observation, ist_reg, " \
                  "object, sub_description, sub_dimension, rdd3, " \
                  "rdd4, rdd5, input_principale, codice_progetto, measures, " \
                  "codice_alternativo, dimension, materials"
    BOM_SEARCH = ['sub_item']
    REQUIRED_BOM = ['sub_item']
    BOM_WARNINGS = ['standard_price']
    BOM_ERRORS = []
    # Default values
    BOM_DEFAULTS = {
    }

    HEADER_PRICELIST_ITEM = ('Articolo', 'Prezzo')
    COLUMNS_PRICELIST_ITEM = "code, price_surcharge"
    REQUIRED_PRICELIST_ITEM = ['code', 'price_surcharge']

    HEADER_CRM = (
        'AZIENDA', 'INDIRIZZO', 'CAP', 'CITTA', 'NAZIONE', 'TELEFONO', 'NOME CONTATTO', 'EMAIL', 'SITO', 'CATEGORIA', 'NOTE'
    )
    COLUMNS_CRM = ['partner_name', 'street', 'zip', 'city', 'country_id', 'phone', 'contact_name', 'email_from', 'website', 'partner_category_id', 'description']
    CRM_SEARCH = ['partner_name', 'email_from']
    REQUIRED_CRM = ['partner_name']
    CRM_WARNINGS = []
    CRM_ERRORS = []

    # Default values
    CRM_DEFAULTS = {
        'optin': True
    }


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
    PARTNER_UNIQUE_OFFICE_CODE = False

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

    HEADER_INVENTORY_ITEM = ('Articolo', 'Quantità', 'Prezzo')
    COLUMNS_INVENTORY_ITEM = "default_code, product_qty, average_cost"
    REQUIRED_INVENTORY_ITEM = ['default_code']
    INVENTORY_PRODUCT_SEARCH = ['default_code']

    HEADER_INVOICE_ITEM = ('Numero documento', 'Data documento', 'Codice Cliente', 'Ragione sociale', 'Codice pagamento', 'Descrizione pagamento', 'Imponibile', 'IVA', 'Totale documento')
    COLUMNS_INVOICE_ITEM = "number_invoice, date_invoice, partner_code, partner_name, payment_code, payment_name, total_untax, total_tax, total_amount"
    REQUIRED_INVOICE_ITEM = ['number_invoice', 'date_invoice', 'partner_code', 'total_untax']


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
    PARTNER_UNIQUE_OFFICE_CODE = False

    HEADER_PRODUCT = (
        'codice', 'nome', 'categoria', 'brand',
        'descrizione vendita', 'uom_i',
        'codiva_acq', 'codiva_cen', 'list_price',
        'ean13', 'fornitore', 'cod__prod__forn_',
        'prezzo_forn_', 'active', 'available_in_pos',
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
    PARTNER_UNIQUE_OFFICE_CODE = True

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


class FormatSix(object):

    HEADER_PRODUCT = (
        "EAN", "DESCRIZIONE", "CATEORIA", "ALIQUOTA IVA",
        "UNITA' DI MISURA", "QUANTITA'", "N.PZ.X CONFEZIONE", "MARCA",
        "PREZZO AL PUBBLICO IVA COMPRESA", "PREZZO PROMOZIONALE IVA COMPRESA", "PREZZO DI COSTO IVA ESCLUSA",
    )

    COLUMNS_PRODUCT = "ean13, name, category, tax, uom, qty_available, pce_package, brand, list_price, list_price_discount, standard_price"

    PRODUCT_SEARCH = ['ean13', 'name']
    REQUIRED_PRODUCT = ['ean13', 'name']
    PRODUCT_WARNINGS = []
    PRODUCT_ERRORS = []

    # Default values
    PRODUCT_DEFAULTS = {
        'supply_method': 'buy',
        'uom_id': 'PCE',
        'type': 'consu',
        'procure_method': 'make_to_order',
        'cost_method': 'standard',
        'sale_ok': True
    }


class FormatOmnitron(object):
    """
    SELECT CodiceProdotto,DescrizioneProdotto,CodiceFornitore,
    DescrizioneProdottoInLingua,AMagazzino,
    IDValuta,PrezzoInValuta,Cambio,
    ListinoFornitore,Sconto,PrezzoAcquisto,ValoreMedio,
    Commento,IDIva,CodiceFornitore2,QtaMagazzino,
    GGConsegna,GestMaga,SpeseTrasporto,
    StatoProdotto,ValoreMedioConSpese,DistintaBaseProduzione,KgMetro
    FROM `bm`.`prodotti`
    WHERE Cancellato=0
    AND DistintaBase=0
    AND StatoProdotto LIKE 'PRODOTTO ATTIVO'
    ORDER BY CodiceProdotto
    INTO OUTFILE 'prodotti_filteredRV.csv'
    FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '#'
    LINES TERMINATED BY '\n';
    """
    HEADER_PRODUCT = (
        "CodiceProdotto", "DescrizioneProdotto", "Categoria", "Codice Fornitore",
        "DescrizioneProdottoInLingua", "AMagazzino",
        "IDValuta", "PrezzoInValuta", "Cambio",
        "ListinoFornitore", "Sconto", "PrezzoAcquisto", "ValoreMedio",
        "Commento", "K-Prezzo Vendita", "IDIva", "QtaMagazzino",
        "GGConsegna", "GestMaga", "SpeseTrasporto",
        "StatoProdotto", "ValoreMedioConSpese", "DistintaBaseProduzione", "KgMetro"
    )

    COLUMNS_PRODUCT = "old_code, description, category, supplier, " \
                      "description_english, omnitron_procurement, " \
                      "none, none1, none2, " \
                      "supplier_price, discount, standard_price, none5, " \
                      "sale_line_warn_msg, k_sale_price, none6, qty, " \
                      "omnitron_produce_delay, omnitron_type, omnitron_delivery_cost, " \
                      "none8, none9, none10, omnitron_weight_per_meter"

    PRODUCT_SEARCH = ['old_code']
    REQUIRED_PRODUCT = ['old_code']
    PRODUCT_WARNINGS = []
    PRODUCT_ERRORS = []

    # Default values
    PRODUCT_DEFAULTS = {
        'supply_method': 'buy',
        'uom': 'PCE',
        # 'type': 'service',
        # 'procure_method': 'make_to_order',
        'cost_method': 'average',
        'sale_ok': True
    }

    HEADER_BOM = (
        "IDDistintaBase", "IDProdottoBase",
        "DescrizioneProdotto", "DescrizioneProdottoInLingua",
        "IDProdottoDB", "CodiceProdottoDB", "DescrizioneProdottoDB",
         "QuantitaNecessaria", "PrezzoAcquisto", "PrezzoVendita",
        "Ordine", "Disponibilita"
    )

    # TODO: control product_qty
    COLUMNS_BOM = """bom_code, old_code,
        product_description, product_description_en,
        none2, sub_item_code, sub_name,
        product_qty, none3, none4,
        sequence, none5
    """
    BOM_PRODUCT_SEARCH = 'old_code'
    BOM_SEARCH = 'bom_code'

    REQUIRED_BOM = ['sub_item_code']
    # BOM_WARNINGS = ['standard_price']
    # BOM_ERRORS = []

    # Default values
    BOM_DEFAULTS = {
    }

    HEADER_CUSTOMER = (
        'IDContatto', 'CodiceContatto',
        'RagioneSociale',
        'IndirizzoSedeLegale', 'CAPSedeLegale', 'LocalitaSedeLegale', 'ProvinciaSedeLegale',
        'RagioneSocialeOperativo',
        'IndirizzoOperativo', 'CAPOperativo', 'LocalitaOperativo', 'ProvinciaOperativo',
        'Telefono', 'Fax', 'Email', 'Web', 'Cellulare',
        'PartitaIVA', 'CodiceFiscale', 'IDPagamento',
        'Pagamento', 'BancaAppoggio', 'ABI', 'CAB', 'ContoCorrente',
        'IDCorriere', 'Corriere', 'IDTrasporto', 'Trasporto',
        'CodiceMerceologico', 'CodiceDivisione',
        'Commenti', 'IDNazione', 'IDRegione', 'IDRespAgente', 'IDTipoCliente',
        'ClienteFornitore', 'Appartenenza',
        'IVAAna', 'AnnoAna', 'IBAN', 'EMailFatture', 'Nazione', 'Valuta'
    )

    COLUMNS = """
        none, code, 
        name,
        street_default, zip_default, city_default, province_default,
        name_delivery,
        street_delivery, zip_delivery, city_delivery, province_delivery,
        phone_default, fax_default, email_default, web_default, mobile_default,
        vat, fiscalcode, none2,
        payment_term, bank, abi, cab, account,
        none4, none5, none6, none7, 
        none8, none9, 
        comment, none10, none11, none12, none13,
        client_supplier, none14,
        none15, none16, iban, email_invoice, country_name, currency
    """
    ADDRESS_TYPE = ('default', 'delivery')
    REQUIRED = ['name']
    PARTNER_SEARCH = ['vat', 'code', 'name']
    PARTNER_UNIQUE_OFFICE_CODE = True


class FormatStandardPriceUpdate(object):
    HEADER_PRODUCT = ("Codice articolo", "Listino Distinte")
    COLUMNS_PRODUCT = "default_code, standard_price"
    PRODUCT_SEARCH = ['default_code']
    REQUIRED_PRODUCT = ['default_code']
    PRODUCT_WARNINGS = []
    PRODUCT_ERRORS = []

    # Default values
    PRODUCT_DEFAULTS = {}


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
    u'INGHILTERRA': 'GB',
    u'REP.SAN MARINO': 'SM',
    u'EMIRATI ARABI': 'AE',
    u'KOREA': 'KR'  # South Korea
}
