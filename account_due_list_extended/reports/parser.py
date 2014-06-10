# -*- coding: utf-8 -*-
##############################################################################
#    
#    Modulo realizzato da Andrea Cometa (info@andreacometa.it)
#    Compatible with OpenERP release 6.1.X
#    Copyright (C) 2012 Andrea Cometa. All Rights Reserved.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#
##############################################################################
import time
from report import report_sxw
import inspect, os
from datetime import datetime
from osv import osv
from osv import fields

class account_due_list_webkit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_due_list_webkit, self).__init__(cr, uid, name, context=context)
        file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
        self.localcontext.update({
            'datetime': datetime,
            'time': time,
            'cr':cr,
            'uid': uid,
            'file_path':file_path,
        })

report_sxw.report_sxw('report.account_due_list.scadenzario',
                       'account.move.line', 
                       'account_due_list_extended/reports/scadenzario.mako',
                       parser=account_due_list_webkit)

