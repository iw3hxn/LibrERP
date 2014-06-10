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

import base64
from osv import osv, fields
from product_metel_sonepar.utils import textEncoding, metelImport
import os


#===============================================================================
# Costanti
#===============================================================================
ASCII_CODE = 'ascii'
#IBM850_CODE = 'ibm850' #(IBM850_CODE, 'ibm850 (cp850)'),
ISO_8859_15_CODE = 'iso-8859-15'

#===============================================================================
# Classi
#===============================================================================
class product_metel_sonepar_import(osv.osv_memory):
    _name = "product.metel.sonepar.import"
    _description = "Import METEL pricelist"
    _inherit = "ir.wizard.screen"
    
    _description = "Import METEL Sonepar pricelist"
    
    # Campi dati della tabella nel DB
    _columns = {
        # Stato in cui si trova il wizard
        'state': fields.selection(
            [ 
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end'),
            ],
            'state',
            required=True,
            translate=False,
            readonly=True,
        ),
                
        # Dati contenuti nel file passato dall'utente codificati
        # in BASE64
        'pricelist_base64': fields.binary('Pricelist file path', required=False, translate=False),
                
        # Dati contenuti nel file passato dall'utente in formato testo
        'pricelist_text': fields.binary('Pricelist file path', required=False, translate=False),
        
        # Codifiche disponibili
        'text_encoding': fields.selection([(ASCII_CODE, 'ascii'), (ISO_8859_15_CODE, 'iso-8859-15'), ('utf-8', 'Unicode 8')], 'Text encoding', required=True, translate=False),
                
        # Righe del listino che danno problemi, memorizzate con la
        # codifica originale
        'preview_text_original': fields.binary('Preview text in original encoding', required=False, translate=False, readonly=True),
                
        # Righe del listino che danno problemi, memorizzate in
        # utf-8 e convertite con la codifica definita dall'utente
        'preview_text_decoded': fields.text('Preview text decoded', required=False, translate=False, readonly=True),
                
        # Fornitore a cui si riferisce il listino
        'supplier': fields.many2one('res.partner', 'Seller', required=True, translate=False),
                
        # Percentuale raggiunta nella converione
        'progress_indicator': fields.integer('Import completato', size=3, translate=False, readonly=True),
        'huge': fields.boolean('File > 25MB'),
        'file_path': fields.char('Percorso file', size=256)
    }
    
    # Valori de default per i campi dati dell'oggetto
    _defaults = {
        'text_encoding': ISO_8859_15_CODE,
        'state': 'import',
        'progress_indicator': 0,
    }
    
    # # # # # # # # # # # # # # # # # # # # # #
    # Azioni associate ai click dei pulsanti  #
    # # # # # # # # # # # # # # # # # # # # # #
    
    def actionCheckEncoding(self, cr, uid, ids, context ):
        # ATTENZIONE: è NECESSARIO passare il contesto alla funzione read
        #             perchè funzioni correttamente!!!!
        record = self.read( cr, uid, ids[0], context=context )
        
        if record['huge']:
            if os.path.exists(record['file_path']):
                self.write(cr, uid, ids, {'state': 'end'}, context=context)
                self.startImport(cr, uid, ids, context)
            else:
                raise osv.except_osv('Attenzione!', 'File non trovato')
        else:
            # Verifichiamo che ci sia stato passato un file da cui prendere i dati
            # Estrazione del contenuto del file in codifica base64
            pricelistBase64 = record['pricelist_base64']
            
            # Check if user supplied the data, if data was not supplied show a message
            if pricelistBase64 is False:
                # Send a message to the user telling that there is a missing field
                raise osv.except_osv('Attenzione!', 'Non è stato impostato il file contenente il listino METEL')
            
            # TODO: verifica impostazione del supplier
                
            # Decodifica del contenuto del file e memorizzazione del testo ottenuto nell'oggetto
            pricelistText = base64.decodestring(pricelistBase64)
            
            self.write(cr, uid, ids, {'pricelist_text': pricelistText}, context=context)
            
            # Decodifica del test in UTF-8 supponendo che l'encoding di partenza sia ASCII,
            # in questo modo è possibile individuare le righe che possono dare problemi di
            # codifica.
            # Le righe problematiche individuate vengono unite in un unica stringa e memorizzate
            # nel'oggetto per poterle utilizzare per la preview
            encodingErrors = textEncoding.checkEncoding(pricelistText, record['text_encoding'])
            previewTextOriginal = '\n'.join(encodingErrors)
            self.write(cr, uid, ids, {'preview_text_original': previewTextOriginal}, context=context )
            
            # Se non ci sono errori di decodifica passiamo allo stato finale
            if len(encodingErrors) == 0:
                # Passaggio allo stato finale
                self.write(cr, uid, ids, {'state': 'end'}, context=context)
                cr.commit()
                # Avvio processo di import
                self.startImport(cr, uid, ids, context)
            
            # Se ci sono errori di decodifica passiamo allo stato preview e diamo all'utente la possibilità
            # di scegliere un'altra codifica
            else:
                # Memorizzazione del testo decodificato secondo quanto indicato dall'utente
                previewTextDecoded = previewTextOriginal.decode(record['text_encoding'], 'replace')
                self.write(cr, uid, ids, {'preview_text_decoded': previewTextDecoded}, context=context )
                
                # Passaggio allo stato preview
                self.write(cr, uid, ids, {'state': 'preview'}, context=context)
        
        # Fine funzione
        return False
    
    def actionStartImport(self, cr, uid, ids, context ):
        # Imposta lo stato finale come prossimo stato
        self.write(cr, uid, ids, {'state': 'end'}, context=context )
        cr.commit()
        # Avvia la procedura di import
        self.startImport(cr, uid, ids, context)
        
        # Fine funzione
        return False
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Azioni associati a cambiamenti nei campi dell'interfaccia (on_change) #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def onChangeEncoding(self, cr, uid, ids, context, text_encoding, state):
        # Se non siamo in stato preview non facciamo niente
        if not ( state == 'preview' ):
            return {}
        
        # ATTENZIONE: è NECESSARIO passare il contesto alla funzione read
        #             perchè funzioni correttamente!!!!
        record = self.read( cr, uid, ids[0], context=context )
        previewTextOriginal = record['preview_text_original']
        
        # Decode original text as new encoding
        previewTextDecoded = previewTextOriginal.decode( text_encoding, 'replace' )
        
        # Update values
        return {
            # Aggiornamento valori
            'value': {
                'preview_text_decoded': previewTextDecoded,
            },
        }
    
    # # # # # # # # # # # #
    # Metodi dell'oggetto #
    # # # # # # # # # # # #
    def startImport(self, cr, uid, ids, context):
        # Avvia l'importatore
        importer = metelImport.MetelImport(cr, uid, ids, context )
        importer.start()

# Create the instance of product_metel_import
product_metel_sonepar_import()

