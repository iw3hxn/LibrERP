# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014 Didotech srl (www.didotech.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.report import report_sxw
from openerp.tools.translate import _
import logging
from datetime import datetime
from openerp.osv import orm

_logger = logging.getLogger(__name__)


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
#        self.localcontext.update({
#            'aaa_lines': self._get_aaa_lines,
#            #'used_tax_codes': {},
#            #'start_date': self._get_start_date,
#        })

    def set_context(self, objects, data, ids, report_type=None):
        self.localcontext.update({
            'fiscal_page_base': data.get('fiscal_page_base'),
            'start_date': data.get('date_start'),
            'fy_name': data.get('fy_name'),
            'type': data.get('type'),
        })
        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)

report_sxw.report_sxw('report.asset_report',
                      'asset_report',
                      'addons/account_asset/templates/asset_report.mako',
                      parser=Parser)