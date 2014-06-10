# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Ivan Bortolatto (ivan.bortolatto at didotech.com)
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
#

from osv import osv, fields
from customer_import.utils import importer
import base64


class filedata_import(osv.osv_memory):
    _name = "filedata.import"
    _description = "Import customers"
    _inherit = "ir.wizard.screen"
    _description = "Import customers from file in .xls format."

    # data fields on DB table
    _columns = {
        # State of this wizard
        'state': fields.selection((('import', 'import'), ('end', 'end')), 'state', required=True, translate=False, readonly=True),
        # file name of import
        'file_name': fields.char('Nome File', size=256),
        # Data of file, in code BASE64
        'content_base64': fields.binary('Customers file path', required=True, translate=False),
        # Data of file, in code text
        'content_text': fields.binary('File Customers', translate=False),
        # progress in perc. of import
        'progress_indicator': fields.integer('Progress import ', size=3, translate=False, readonly=True),
    }
    # default value for data fields of object
    _defaults = {
        'state': 'import',
        'progress_indicator': 0,
    }
    
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
            raise osv.except_osv('Attenzione!', 'Non è stato impostato il file contenente i Clienti')
            
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
        result_data = self.read(cr, uid, ids[0], context=context)
        
        # Start import
        data_importer = importer.ImportFile(cr, uid, ids, context, result_data['content_text'])
        data_importer.start()
        return False

filedata_import()
