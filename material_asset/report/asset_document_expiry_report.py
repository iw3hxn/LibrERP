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


class empty_document_type():
    name = ''


class empty_asset():
    name = ''
    
    
class empty_document():
    name = ''
    document_type_id = empty_document_type()
    valid_start_date = ''
    valid_end_date = ''
    
    
class asset_document_expiry_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(asset_document_expiry_report, self).__init__(cr, uid, name, context=context)
        self.month = False
        self.year = False
        self.asset_obj = pooler.get_pool(self.cr.dbname).get('asset.asset')
        self.doc_obj = pooler.get_pool(self.cr.dbname).get('asset.document')
        self.localcontext.update({
            'time': time,
            'get_asset': self.get_asset,
            'get_asset_documents': self.get_asset_documents,
        })
        
    def get_asset(self, form):
        result = []
        periods = []
        
        self.date_from = form['date_from']
        self.date_to = form['date_to']
        self.category = form.get("category_id", False)
        
        self.search_array = [('valid_end_date', '>=', self.date_from), ('valid_end_date', '<=', self.date_to)]
        if self.category:
            self.search_array.append(('document_type_id', '=', self.category))
        doc_ids = self.doc_obj.search(self.cr, self.uid, self.search_array)
        docs = self.doc_obj.browse(self.cr, self.uid, doc_ids)
        asset_ids = [doc.asset_id.id for doc in docs]
        result = self.asset_obj.browse(self.cr, self.uid, asset_ids)
        
        if result:
            return result
        else:
            return [empty_asset(),]
    
    def get_asset_documents(self, obj):
        result = []
        periods = []
        
        if obj.name:
            self.search_array.append(('asset_id', '=', obj.id))
            doc_ids = self.doc_obj.search(self.cr, self.uid, self.search_array)
            result = self.doc_obj.browse(self.cr, self.uid, doc_ids)
            return result
        else:
            return [empty_document(),]

report_sxw.report_sxw('report.asset.document.expiry', 'asset.asset', 'addons/material_asset/report/asset_document_expiry_report.rml', parser=asset_document_expiry_report, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

