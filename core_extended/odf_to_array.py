# Copyright 2011 Marco Conti
# Copyright 2015 Andrei Levin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Thanks to grt for the fixes
#
# https://github.com/marcoconti83/read-ods-with-odfpy/blob/master/odf-to-array.py
#

import logging

_logger = logging.getLogger(__name__)

try:
    import odf.opendocument
    from odf.table import *
    from odf.text import P
except:
    _logger.error('Cannot `import odfpy`')

from collections import OrderedDict


class ODSReader(OrderedDict):
    # loads the file
    def __init__(self, file):
        super(ODSReader, self).__init__()
        self.doc = odf.opendocument.load(file)
        map(self.read_sheet, self.doc.spreadsheet.getElementsByType(Table))

    # reads a sheet in the sheet dictionary, storing each sheet as an array (rows) of arrays (columns)
    def read_sheet(self, sheet):
        name = sheet.getAttribute("name")
        rows = sheet.getElementsByType(TableRow)
        table = []
        max_row_length = 0

        # for each row
        for row in rows:
            arr_cells = []
            cells = row.getElementsByType(TableCell)
            row_length = 0
            empty_cells = 0

            # for each cell
            for cell in cells:
                # repeated value?
                repeat = cell.getAttribute("numbercolumnsrepeated")
                if repeat:
                    repeat = int(repeat)
                else:
                    repeat = 1

                ps = cell.getElementsByType(P)
                text_content = ""

                # for each text node
                for p in ps:
                    for n in p.childNodes:
                        if n.nodeType == 3:
                            text_content += unicode(n.data)

                if text_content:
                    row_length += repeat
                    if empty_cells:
                        map(lambda x: arr_cells.append(''), range(empty_cells))
                        row_length += empty_cells
                        empty_cells = 0
                    map(lambda x: arr_cells.append(text_content), range(repeat))
                else:
                    empty_cells += repeat

            # if row contains something
            if arr_cells:
                if row_length <= max_row_length:
                    if repeat + row_length > max_row_length:
                        repeat = max_row_length - row_length
                    map(lambda x: arr_cells.append(text_content), range(repeat))
                table.append(arr_cells)

            if row_length > max_row_length:
                max_row_length = row_length

        self[name] = table

    # returns a sheet as an array (rows) of arrays (columns)
    def sheet_by_name(self, name):
        return self[name]

    def sheet_by_index(self, index):
        return self.items()[index][1]
