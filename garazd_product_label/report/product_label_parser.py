# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
import time

_logger = logging.getLogger(__name__)

from report import report_sxw


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'create_product_tree': self.create_product_tree,
        })
        self.context = context
        self.sale_tree = False

    def create_product_tree(self, product_line):

        sales = []

        for line in product_line:
            if line.selected:
                for number in range(0, line.qty):
                    sales.append(line)

        self.sale_tree = sales
        return sales
