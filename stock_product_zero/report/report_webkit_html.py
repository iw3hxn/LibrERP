# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

import time
from openerp.report import report_sxw
from openerp.osv import osv

class report_webkit_html(report_sxw.rml_parse):

#inventory value for product
    def _get_product_values(self):
        res = {}
        product_obj = self.pool['product.product']
        product_ids = product_obj.search(self.cr, self.uid, [])
        for product in product_obj.browse(self.cr, self.uid, product_ids):
            if product.cost_price:
                res.update({product.id: product.cost_price})
            else:
                res.update({product.id: 0.0})
        return res

    def __init__(self, cr, uid, name, context):
        super(report_webkit_html, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'get_products': self._get_product_values,
        })

    def set_context(self, objects, data, ids, report_type=None):
        return super(report_webkit_html, self).set_context(objects, data, ids, report_type=report_type)

report_sxw.report_sxw('report.stock.inventory.webkit',
                       'stock.inventory',
                       'addons/stock_product_zero/report/stock_inventory.mako',
                       parser=report_webkit_html)
