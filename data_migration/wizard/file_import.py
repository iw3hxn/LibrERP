# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Didotech SRL (info at didotech.com)
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

from osv import osv, fields
from data_migration.utils import partner_importer
from data_migration.utils import product_importer
import base64
from tools.translate import _


class filedata_import(osv.osv_memory):
    _name = "filedata.import"
    _inherit = "ir.wizard.screen"
    
    # # # # # # # # # # # # # #
    # action of button click  #
    # # # # # # # # # # # # # #
    def actionCheckEncoding(self, cr, uid, ids, context):
        # WARNING: Context is required, for correct functionally of 'read'.
        record = self.read(cr, uid, ids[0], context=context)

        # Extration file content, encoded in base64
        contentBase64 = record['content_base64']

        # Check if user supplied the data, if data was not supplied show a message
        if not contentBase64:
            # Send a message to the user telling that there is a missing field
            raise osv.except_osv('Attenzione!', 'Non è stato selezionato il file da importare')
            
        # Decoding content of file and store the resulting text in object
        decodedText = base64.decodestring(contentBase64)

        vals = {
            'content_text': decodedText,
            'file_name': record['file_name'],
        }
        self.write(cr, uid, ids, vals, context=context)

        self.actionStartImport(cr, uid, ids, context)
        return False
    
    def actionStartImport(self, cr, uid, ids, context):
        # Set 'end' as a next state
        self.write(cr, uid, ids, {'state': 'end'}, context=context)

        # for OE 6.1; memory object not move data in other thread - move data in parameters
        cr.commit()
        # Start import
        data_importer = self.importer.ImportFile(cr, uid, ids, context)
        data_importer.start()
        return False


class partner_import(filedata_import):
    _name = "partner.import"
    _description = "Import partner from a file in .xls format."
    
    importer = partner_importer

    # data fields on DB table
    _columns = {
        # State of this wizard
        'state': fields.selection((('import', 'import'), ('end', 'end')), 'state', required=True, translate=False, readonly=True),
        'format': fields.selection((
            ('FormatOne', _('Format One')),
            ('FormatTwo', _('Format Two')),
            ('FormatThree', _('Format Three')),
        ), 'Formato Dati', required=True, readonly=False),
        # file name of import
        'file_name': fields.char('Nome File', size=256),
        # Data of file, in code BASE64
        'content_base64': fields.binary('Partner file path', required=True, translate=False),
        # Data of file, in code text
        'content_text': fields.binary('File Partner', translate=False),
        'progress_indicator': fields.integer('Progress import ', size=3, translate=False, readonly=True),
        'partner_type': fields.selection((('customer', 'Customer'), ('supplier', 'Supplier')), 'Partner Type', required=True),
        'strict': fields.boolean('Strict', help="Use more strict (and more slow) data check")
    }
    # default value for data fields of object
    _defaults = {
        'state': 'import',
        'progress_indicator': 0,
        'strict': False
    }


class product_import(filedata_import):
    _name = "product.import"
    _description = "Import products from file in .csv format."
    
    importer = product_importer

    # data fields on DB table
    _columns = {
        # State of this wizard
        'state': fields.selection((('import', 'import'), ('preview', 'preview'), ('end', 'end')), 'state', required=True, translate=False, readonly=True),
        'format': fields.selection((
            ('FormatOne', _('Format One')),
            #('FormatTwo', _('Format Two')),
            ('FormatThree', _('Format Three')),
            ('FormatFour', _('Format Four')),
        ), 'Formato Dati', required=True, readonly=False),

        # Data of file, in code BASE64
        'content_base64': fields.binary('Products file path', required=False, translate=False),
        'file_name': fields.char('File Name', size=256),
        # Data of file, in code text
        'content_text': fields.binary('File Partner', required=False, translate=False),
        # Codecs
        #'text_encoding': fields.selection([(ASCII_CODE, 'ascii'), (ISO_8859_15_CODE, 'iso-8859-15'), ('utf-8', 'Unicode 8')], 'Text encoding', required=True, translate=False),
        # problem's row of product. original code
        'preview_text_original': fields.binary('Preview text original', required=False, translate=False, readonly=True),
        # problem's row of product. decoded
        'preview_text_decoded': fields.text('Preview text decoded', required=False, translate=False, readonly=True),
        # Supplier
        #'supplier': fields.many2one('res.partner', 'Seller', required=True, translate=False),
        'progress_indicator': fields.integer('Progress import ', size=3, translate=False, readonly=True),
        #'file_path': fields.char('Percorso file', size=256)
    }
    # default value for data fields of object
    _defaults = {
        #'text_encoding': ISO_8859_15_CODE,
        'state': 'import',
        'progress_indicator': 0,
    }
