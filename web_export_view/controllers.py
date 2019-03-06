# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>)
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

try:
    import json
except ImportError:
    import simplejson as json
import re
from cStringIO import StringIO
try:
    import xlwt
except ImportError:
    xlwt = None

import web.common.http as openerpweb
from web.controllers.main import ExcelExport
from datetime import datetime


class ExcelExportView(ExcelExport):
    _cp_path = '/web/export/xls_view'

    def from_data(self, fields, rows, separators):
        workbook = xlwt.Workbook(style_compression=2)
        worksheet = workbook.add_sheet('Sheet 1')

        # style for header
        style_header = xlwt.easyxf('font: bold on; pattern: pattern solid, fore-colour grey25; align: horiz center')
        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname, style_header)
            worksheet.col(i).width = len(fieldname) * 300

        style = xlwt.easyxf('align: wrap yes')
        number_pattern = re.compile(r"^-?[\d%s]+(\%s\d+)?$" % (
            separators['thousands_sep'],
            separators['decimal_point']
        ))
        date_pattern = re.compile('^\d{2}[-/]\d{2}[-/]\d{4}$')

        for row_index, row in enumerate(rows):
            for cell_index, cell_value in enumerate(row):
                if isinstance(cell_value, basestring):
                    cell_value = re.sub("\r", " ", cell_value)
                    is_number = number_pattern.match(cell_value)
                    # If starting with '0' don't convert to number (for avoiding number conversion of default_code)
                    if is_number and cell_value and cell_value[0] != '0':
                        cell_value = float(
                            cell_value.replace(
                                separators.get('thousands_sep', ''), ''
                            ).replace(
                                separators['decimal_point'], '.'
                            ) or 0.00
                        )
                        # style = xlwt.easyxf(num_format_str='#,##0.00')
                        len_cell = len('{num}'.format(num=cell_value)) * 500
                        style = xlwt.easyxf(num_format_str='#,##0.00;[RED]-#,##0.00')
                    elif date_pattern.match(cell_value):
                        try:
                            cell_value = datetime.strptime(cell_value, separators['date_format'])
                            # style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
                            style = xlwt.easyxf(num_format_str='d mmm yyyy')
                        except Exception as e:
                            cell_value = re.sub("\r", " ", cell_value)
                        len_cell = 4000
                    else:
                        len_cell = len(cell_value) * 250
                    if worksheet.col(cell_index).width < len_cell:
                        if len_cell < 65535:
                            worksheet.col(cell_index).width = len_cell

                if cell_value is False:
                    cell_value = None
                worksheet.write(row_index + 1, cell_index, cell_value, style)

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data

    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])

        context = req.session.eval_context(req.context)
        lang = context.get('lang', 'en_US')
        Model = req.session.model('res.lang')
        Object = req.session.model('ir.model')
        lang_ids = Model.search([['code', '=', lang]], context=context)
        record = Model.read(lang_ids, ['decimal_point', 'thousands_sep', 'date_format'], context)
        object_ids = Object.search([['model', '=', model]], context=context)
        if object_ids:
            model = Object.read(object_ids[0], ['name'], context)['name'].replace(' ', '_')
        return req.make_response(
            self.from_data(columns_headers, rows, record[0]),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"' % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': int(token)})
