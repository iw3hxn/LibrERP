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
            'italian_number': self._get_italian_number,
            'location_names': self._get_location_name,
            'test_simple': self._get_test_simple,
            'test_only_partner': self._get_only_partner,
            'test_only_journal': self._get_only_journal,
            'test_full': self._get_full
        })
        self.context = context
        self.sale_tree = False
        self.show_partner = self.context.get('show_partner', False)
        self.show_journal = self.context.get('show_journal', False)

    def _get_test_simple(self):
        return not self.show_partner and not self.show_journal

    def _get_only_partner(self):
        return self.show_partner and not self.show_journal

    def _get_only_journal(self):
        return not self.show_partner and self.show_journal

    def _get_full(self):
        return self.show_partner and self.show_journal

    def _get_location_name(self):
        location_name = self.context.get('location_name', 'booh')
        return location_name

    def create_product_tree(self):

        sales = []
        for line in self.pool['stock.move.group'].browse(self.cr, self.uid, self.context['move_groups'], self.context):
            sales.append(line)

        self.sale_tree = sales
        return sales

    def _get_italian_number(self, obj, field, precision=False, no_zero=False):

        number = obj[field]
        precision = precision or obj._model._all_columns[field].column.digits[1]
        if not number and no_zero:
            return ''
        elif not number:
            return '0,00'

        if number < 0:
            sign = '-'
        else:
            sign = ''
        ## Requires Python >= 2.7:
        # before, after = "{:.{digits}f}".format(number, digits=precision).split('.')
        ## Works with Python 2.6:
        if precision:
            before, after = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')
        else:
            before = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')[0]
            after = ''
        belist = []
        end = len(before)
        for i in range(3, len(before) + 3, 3):
            start = len(before) - i
            if start < 0:
                start = 0
            belist.append(before[start: end])
            end = len(before) - i
        before = '.'.join(reversed(belist))

        if no_zero and int(number) == float(number) or precision == 0:
            return sign + before
        else:
            return sign + before + ',' + after
