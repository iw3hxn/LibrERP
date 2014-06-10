# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Andrei Levin (andrei.levin at didotech.com)
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
##############################################################################

import pooler
import datetime
import threading
from tools.translate import _
import math
import time
import io

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


# Constants

# Tempo di consegna materiale espresso in giorni lavorativi
# come da standard Manuale Listino Rel. 1.1 - rev.10 - Marzo 2011
# http://www.metel.it/stc/DownloadPubFile.pub_do/(id)402882a82ed6bcdd012ed77d44190002/Manuale_Listino_Rel_1.1_rev_10_Marzo_2011.zip
LEADTIME_CONVERSION_TABLE = {
    # I numeri esprimono direttamente i giorni
    # lavorativi previsti per la consegna
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    
    # Le lettere esprimono le settimane previste per la consegna,
    # ogni settimana comprende 5 giorni lavorativi e si parte da
    # due settimane (quindi A = 2 sett = 10 giorni lavorativi)
    'A': 2 * 5,
    'B': 3 * 5,
    'C': 4 * 5,
    'D': 5 * 5,
    'E': 6 * 5,
    'F': 7 * 5,
    'G': 8 * 5,
    'H': 9 * 5,
    'I': 10 * 5,
    'J': 11 * 5,
    'K': 12 * 5,
    'L': 13 * 5,
    'M': 14 * 5,
    'N': 15 * 5,
    'O': 16 * 5,
    'P': 17 * 5,
    'Q': 18 * 5,
    'R': 19 * 5,
    'S': 20 * 5,
    'T': 21 * 5,
    'U': 22 * 5,
    'V': 23 * 5,
    'W': 24 * 5,
    'X': 25 * 5,
    'Y': 26 * 5,
    'Z': 27 * 5,
}

class MetelImport(threading.Thread):
    def __init__(self, cr, uid, ids, context):
        
        # Inizializzazione superclasse
        threading.Thread.__init__(self)
        
        # Inizializzazione classe MetelImport
        self.uid = uid
        
        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        
        # Necessario creare un nuovo cursor per il thread,
        # quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile
        # all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()
        
        self.productMetelImportID = ids[0]
        self.importedLines = 0
        
        self.context = context
        
        self.manufacturerID = None
        
        # Contatori dei nuovi prodotti inseriti e dei prodotti aggiornati,
        # vengono utilizzati per compilare il rapporto alla terminazione
        # del processo di import
        self.uo_new = 0
        self.uo_update = 0
    
    def run(self):
        # Recupera il record dal database
        self.product_metel_sonepar_obj = self.pool.get('product.metel.sonepar.import')
        self.productMetelImportRecord = self.product_metel_sonepar_obj.browse(self.cr, self.uid, self.productMetelImportID, context = self.context)
        
        # Memorizza l'ID del supplier
        self.supplierID = self.productMetelImportRecord.supplier.id
        
        # Decodifica il testo in base alla codifica fornita dall'utente
        try:
            if self.productMetelImportRecord.huge:
                #metelPricelistRecords = io.open(self.productMetelImportRecord.file_path, encoding='iso-8859-15')
                #metelPricelistRecords = io.open(self.productMetelImportRecord.file_path, encoding='utf-8')
                metelPricelistRecords = io.open(self.productMetelImportRecord.file_path, encoding=self.productMetelImportRecord.text_encoding)
            else:
                pricelistText = self.productMetelImportRecord.pricelist_text.decode(self.productMetelImportRecord.text_encoding)
                metelPricelistRecords = io.StringIO(pricelistText)
        except UnicodeDecodeError as exception:
            self.notifyError(exception)
            return
        
        # Elaborazione dell'intestazione.
        ##try:
        ##    self.processMetelPricelistHeader()
        ##except ManufacturerNotFoundException as exception:
        ##    self.notifyError(exception)
        ##    return
        ##except MetelCategoryNotFoundException as exception:
        ##    self.notifyError(exception)
        ##    return
        
        # Elaborazione del listino prezzi
        try:
            # Importa il listino
            self.processMetelPricelist(self.cr, self.uid, metelPricelistRecords)
            
            # Genera il report sull'importazione
            self.notifySuccessfulImport()
            
            # Salva le modifiche sul database e chiude la connessione
            self.cr.commit()
            self.cr.close()
        except Exception as e:
            # Annulla le modifiche fatte
            self.cr.rollback()
            self.cr.commit()
            
            message = "Error occured at line %s" % self.importedLines + "\nError details:\n\n" + str(e)
            
            self.notifyError(message)
    
    ##def processMetelPricelistHeader(self):
    ##    # Text of the Metel Pricelist Header
    ##    header = self.metelPricelistRecords.pop(0)
    ##    
    ##    # Header decoding
    ##    self.metel = header[0:20].strip()
    ##    self.prod = header[20:23]
    ##    self.desc = header[56:125].strip()
    ##    self.date_start = datetime.date(int(header[40:44]), int(header[44:46]), int(header[46:48]))
    ##    self.last_change = datetime.date(int(header[48:52]), int(header[52:54]), int(header[54:56]))
    ##    
    ##    # Search a partner matching Metel code found in the header
    ##    manufacturerIDs = self.pool.get('res.partner').search(self.cr, self.uid, [('metel_code', '=', self.prod)])
    ##    
    ##    # If there is a matching partner then retrive its Metel category
    ##    if manufacturerIDs:
    ##        
    ##        # Extract partner ID from the list
    ##        self.manufacturerID = manufacturerIDs[0]
    ##        
    ##        # Retrive object representation for partner record
    ##        resPartnerTable = self.pool.get('res.partner')
    ##        self.manufacturerObject = resPartnerTable.browse(self.cr, self.uid, self.manufacturerID)
    ##        
    ##        # Retrive import category for the partner
    ##        metelCategory = self.manufacturerObject.metel_category
    ##        
    ##        # If partner has a metel category assigned store it for later use
    ##        if metelCategory:
    ##            self.cat_id = metelCategory.id
    ##        
    ##        # If partner does not have a metel category assigned raise an exception
    ##        else:
    ##            raise MetelCategoryNotFoundException('Partner %s with metel code %s does not have a Metel category assigned.' % (self.manufacturerObject.name, self.manufacturerObject.metel_code))
    ##    # If there is not a matching partner raise an exception
    ##    else:
    ##        # Set partner_id to None since it is used later to
    ##        # generate the error report
    ##        self.manufacturerID = None
    ##        
    ##        # Lancio eccezione
    ##        raise ManufacturerNotFoundException('Manufacturer with metel code %s does not exists' % self.prod )
        
    def processMetelPricelist(self, cr, uid, metelPricelistRecords):
        for line in metelPricelistRecords:
            # If line is empty jump to the next one
            if len(line.strip()) == 0:
                continue
            
            _logger.debug(u'{0} {1}'.format(self.importedLines, line))
            
            # Import row
            self.ImportRow(cr, uid, line)
            
            # Update counter of imported lines
            self.importedLines = self.importedLines + 1
            if self.importedLines % 100 == 0:
                _logger.debug(u'*************** Committing... ****************')
                cr.commit()
        
    def ImportRow(self, cr, uid, line):
        empty = line[0:15]
        description = line[15:50].strip()
        list_price = float(line[50:62])/100.00
        empty = line[62:63]
        ## Prezzo netto:
        std_price = float(line[63:75])/100.00
        uom = line[75:77]
        #print line[0:83]
        multiplier = int(line[77:83])
        family_stat = line[83:101]
        discount_code = line[101:119]
        bar_code_sonepar = line[119:137]
        product_code = line[137:156].strip()
        empty = line[156:280]
        empty = line[280:292]
        
        
        #print description, list_price, std_price, uom, multiplier, product_code
        
        list_price /= multiplier
        std_price /= multiplier
        
        qmin = multiplier
        
        if len(product_code) <= 0:
            return
        
        # Check if product is already registered in the DB, in this case the product need to be updated, else we must
        # create it
        ##product_ids = self.pool.get('product.product').search(self.cr, self.uid, [('manufacturer', '=', self.manufacturerID), ("manufacturer_pref", '=', product_code)])
        product_ids = self.pool.get('product.product').search(self.cr, self.uid, [("manufacturer_pref", '=', product_code)])
        
        # If a matchinf product is already in the DB proceed with the update....
        if product_ids:
            for product_id in product_ids:
                self.uo_update += 1
                
                product = self.pool.get('product.product').write(self.cr, self.uid, product_id, {'standard_price': std_price, 'list_price': list_price})
                
                # is there a matching supplier info ?
                product_template_id = self.getProductTemplateID(product_id)
                #supplier_id = self.pool.get('product.supplierinfo').search(self.cr, self.uid, [('product_id', '=', product_template_id )])
                supplier_id = self.pool.get('product.supplierinfo').search(self.cr, self.uid, [('product_id', '=', product_template_id ), ('name', '=', self.supplierID)])
                
                #updated supplier info with leadtime and minimun quantity
                if supplier_id:
                    # TODO: controllare cosa fare con qty e min_qty
                    ##supplier = self.pool.get('product.supplierinfo').write(self.cr, self.uid, supplier_id[0], {'qty': qmin, 'min_qty': qmin, 'delay': leadtime})
                    supplier = self.pool.get('product.supplierinfo').write(self.cr, self.uid, supplier_id[0], {'qty': qmin, 'min_qty': qmin})
                # create the supplier info for the supplier
                else:
                    # Get the product_tempalte ID, the supplier is associated
                    # with the product template not with the product itsef
                    #product_template_id = self.getProductTemplateID(product_id[0])
                    supplier = self.pool.get('product.supplierinfo').create(self.cr, self.uid,
                    {
                        'product_id': product_template_id,
                        'qty': qmin,
                        'min_qty': qmin,
                        #'delay': leadtime,
                        'name': self.supplierID,
                        'product_code': product_code,
                        'product_name': description,
                    })
            
        # ....else create the new product and the new suppliers entries.
        # We use the code and the description of the manufacturer
        else:
            self.uo_new += 1
            
            #product_cat = self.GetDiscountFamily(family_discount)
            product_uom = self.GetUOM(uom)
            
            product = self.pool.get('product.product').create(self.cr, self.uid,
            {
                'default_code': product_code,
                'name': description,
                #'ean13': ean13,
                #'manufacturer': self.manufacturerID,
                'manufacturer_pref': product_code,
                'manufacturer_pname': description,
                'standard_price': std_price,
                'list_price': list_price,
                'type': 'product',
                'uom_id': product_uom,
                'uom_po_id': product_uom,
            })
            
            # Get the product_template ID, the supplier is associated
            # with the product template not with the product itsef
            product_template_id = self.getProductTemplateID(product)
            
            # create the supplier info for the manufacturer
            supplier = self.pool.get('product.supplierinfo').create(self.cr, self.uid,
            {
                'product_id': product_template_id,
                'qty': qmin,
                'min_qty': qmin,
                #'delay': leadtime,
                'name': self.supplierID,
                'product_code': product_code,
                'product_name': description,
            })
            
    def notifySuccessfulImport(self):
        body = _(u"Imported products: %d \nUpdated products: %d") % (self.uo_new, self.uo_update)
        request = self.pool.get('res.request')
        request.create(self.cr, self.uid, {
            'name': _("Metel Import Completed"),
            'act_from': self.uid,
            'act_to': self.uid,
            #'ref_partner_id': self.manufacturerID,
            'state': 'waiting',
            'body': body,
            'active': True,
        })
        #print body
        _logger.debug(body)
            
    def notifyError(self, errorDescription):
        body = str(errorDescription)
        request = self.pool.get('res.request')
        request.create(
            self.cr,
            self.uid, 
            vals = {
                'name': _("Metel Import Error"),
                'act_from': self.uid,
                'act_to': self.uid,
                #'ref_partner_id': self.manufacturerID,
                'state': 'waiting',
                'body': body,
                'active': True,
            },
            context = self.context,
        )
        #print body
        _logger.debug(body)
        
        # Salva il messaggio di errore nel database e chiudi la connessione
        self.cr.commit()
        self.cr.close()
    
    #===========================================================================
    # Utility methods
    #===========================================================================
    def getProductTemplateID(self, product_id):
        # Get the product_tempalte ID
        
        # Retrive the record associated with the product id
        productObject = self.pool.get('product.product').browse(self.cr, self.uid, product_id)
        
        # Retrive the template id
        product_template_id = productObject.product_tmpl_id.id
        
        # Return the template id
        return product_template_id
    # end getProductTemplateID()
    
    def GetDiscountFamily(self, name):
        '''Get the category that match the specified discount family, in not found create it
        Args:
          name: Discount family name
          
        Returns:
          The category ID of the product
        '''
        if len(name) > 0:
            #is there a matching category ?
            family_id = self.pool.get('product.category').search(self.cr, self.uid, [('name', '=', name), ("parent_id", '=', self.cat_id)])
            
            # family found
            if family_id:
                return family_id[0]
            #family discount not found, create it
            else:
                return self.pool.get('product.category').create(self.cr, self.uid,
                {
                    'name': name,
                    'parent_id': self.cat_id,
                })
        
        #if category name is empty return the main import category ID
        return self.cat_id

    def GetUOM(self, uom):
        '''Get the unity of measure specified, in not found create it
        
        Args:
          name: UOM name
          
        Returns:
          The UOM ID of the product
        '''
        
        if len(uom) == 0:
            return 0
        
        #is there a matching category ?
        uom_id = self.pool.get('product.uom').search(self.cr, self.uid, [('name', '=', uom.lower())])
        if uom_id:
            return uom_id[0]
        else:
            uom_cat_ids = self.pool.get('product.uom.categ').search(self.cr, self.uid, [('name', '=', 'Unit')])
            return self.pool.get('product.uom').create(self.cr, self.uid,
            {
                'name': uom,
                'category_id': uom_cat_ids[0],
                'factor': 1,
            })
        return 0

#===============================================================================
# Eccezioni
#===============================================================================
class ManufacturerNotFoundException(Exception):
    pass
# end class MetelHeaderException

class MetelCategoryNotFoundException(Exception):
    pass
# end class MetelLineException