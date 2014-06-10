# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Dhaval Patel (dhpatel82 at gmail.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
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
import time
from report import report_sxw
import pooler
import datetime

class res_car_document_expiry_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(res_car_document_expiry_report, self).__init__(cr, uid, name, context=context)
        self.month = False
        self.year = False
        self.localcontext.update({
            'time': time,
            'get_car': self.get_car,
            'get_car_documents': self.get_car_documents,
        })
    def get_car(self, form):
        result = []
        periods = []
        car = pooler.get_pool(self.cr.dbname).get('res.car')
        car_ids = form['ids']
        result = car.browse(self.cr,self.uid, car_ids)
        self.date_from = form['date_from']
        self.date_to = form['date_to']
        return result
    def get_car_documents(self, obj):
        result = []
        periods = []
        doc = pooler.get_pool(self.cr.dbname).get('res.car.document')
        doc_ids = doc.search(self.cr, self.uid, [('car_id','=',obj.id), ('valid_end_date', '>=', self.date_from), ('valid_end_date', '<=', self.date_to)])
        result = doc.browse(self.cr, self.uid, doc_ids)
        return result

report_sxw.report_sxw('report.res.car.document.expiry', 'res.car', 'addons/hr_auto/report/res_car_document_expiry_report.rml', parser=res_car_document_expiry_report, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

