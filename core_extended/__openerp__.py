# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2018 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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

{
    "name": "Core extended",
    "version": "2.2.18.2",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": "Base",
    "description": """
        Module extendes OpenERP core functionality:
        account - add column 'origin_document' to account.invoice.line

        ir_sequence - add functions:
            current_number(cr, uid, sequence_id)
            go_back(cr, uid, sequence_id, steps_back=1)
            create() will set code to the value find in context dictionary (if value is present in context)
            
        ir_attachment - add function
            get_as_zip(cr, uid, ids, log=False, encode=True, compress=True)
            
        ordereddict - Backport of OrderedDict() class that runs on Python 2.4, 2.5, 2.6, 2.7 and pypy.
        
        wkf_service - add function
            trg_last_action(uid, model, obj_id, cr) - this function is useful when debugging a workflow related problems 
        
        orm - Monkey Patched function name_get(). Now it will throw an error if 'name' or name_get() are not defined, but will not break a code execution.
            Code will break only if 'debug_mode' defined in config file.
            
        bizdatetime - simple library for performing business day arithmetic:
            policy = Policy(weekends=(SAT, SUN), holidays=(date(2011,7,1),))
            policy.biz_day_delta(date(2011, 6, 30), date(2011, 7, 4)) # one holiday, one weekend between

        odf_to_array - class that permits reading of Open Document spreadsheet

        file_manipulation - contains function that recognise Excel, Open Document and CSV documents
            and return them as list of rows. Additional python modules are required:
            'xls', 'xlsb' - requires module xlrd
            'xlsx', 'xlsm', 'xltx', 'xltm' - requires openpyxl
            'ods' - requires odf
            'csv' - uses module csv included in standard Python distribution

        create group - View Reporting
        
        dict_cache - Dictionary class extended with empty() method
        
        redis - Dictionary-like class to work with Redis. Use database with index 0 for database to index mapping
            Requires walrus module for communication with Redis

    """,
    "depends": [
        'base',
        'account'
    ],
    "data": [
        'security/security.xml',
        'views/ir_model_view.xml',
    ],

    "active": False,
    "installable": True,
    'external_dependencies': {
        'python': [
            'zlib',
        ]  
    }
}
