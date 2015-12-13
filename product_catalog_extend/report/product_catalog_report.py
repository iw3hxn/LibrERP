# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011 Didotech Inc. (<http://www.didotech.com>)
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

import time
from report import report_sxw
import pooler
import pprint

from openerp.osv import orm, fields
import decimal_precision as dp

pp = pprint.PrettyPrinter(indent=4)

#try:
#    from cStringIO import StringIO
#    _hush_pyflakes = [StringIO]
#except ImportError:
#    from StringIO import StringIO


class product_product(orm.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    def _product_price2(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        quantity = context.get('quantity') or 1.0
        pricelist = context.get('pricelist2', False)
        if pricelist:
            for product_id in ids:
                try:
                    price = self.pool['product.pricelist'].price_get(cr, uid, [pricelist], product_id, quantity, context=context)[pricelist]
                except:
                    price = 0.0
                res[product_id] = price
        for product_id in ids:
            res.setdefault(product_id, 0.0)
        return res

    _columns = {
        'price2': fields.function(_product_price2, method=True, type='float', string='Pricelist', digits_compute=dp.get_precision('Sale Price')),
    }


class product_catalog_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(product_catalog_report, self).__init__(cr, uid, name, context=context)
        self.month = False
        self.year = False
        
        self.localcontext.update({
            'time': time,
            'get_categories': self.get_categories,
            'get_product': self.get_products,
            'get_pricelist_name': self.get_pricelist_name,
        })
        
    def setCat(self, cats):
        lst = []
        for cat in self.pool['product.category'].browse(self.cr, self.uid, cats):
            if cat.id not in lst:
                lst.append(cat.id)
                for child_id in cat.child_id:
                    child_ids = self.setCat([child_id.id])
                    lst.extend(child_ids)
        return lst

    def get_pricelist_name(self, form, pricelist_id):
        pricelist_data = self.pool['product.pricelist'].browse(self.cr, self.uid, form[pricelist_id][0])
        return '%s (%s)' % (pricelist_data.name, pricelist_data.currency_id.name)

    def get_erase(self, lista):
        for i in lista:
            if lista.count(i) > 1:
                lista.remove(i)
                # Elimina()
        return lista

    def get_categories(self, form):
        category = form.get('category_id', False)
        self.pricelist_id = form.get('pricelist_id', False)
        self.pricelist_id2 = form.get('pricelist_id2', False)
        lst = []
        if not category:
            lst = self.pool['product.category'].search(self.cr, self.uid, [])
            return self.pool['product.category'].browse(self.cr, self.uid, lst)

        lst = self.setCat([category[0]])
        # cat_ids = self.pool['product.category'].search(self.cr, self.uid, [('id', 'in', lst)])
        cat_ids = self.get_erase(lst)

        tmpCat_ids = []
        for cat in cat_ids:
            prod_ids = self.pool['product.template'].search(self.cr, self.uid, [('categ_id', '=', cat)])
            if len(prod_ids):
                tmpCat_ids.append(cat)
        cats = self.pool['product.category'].browse(self.cr, self.uid, tmpCat_ids)
        return cats

    def get_products(self, c):
        prod_tmpIDs = self.pool.get('product.template').search(self.cr, self.uid, [('categ_id', '=', c), ])
        prod_ids = self.pool.get('product.product').search(self.cr, self.uid, [
            ('product_tmpl_id', 'in', prod_tmpIDs),
            ('sale_ok', '=', True),
            ('catalog', '=', True)
        ], order='name')
        price_context = {}
        if self.pricelist_id:
            price_context['pricelist'] = self.pricelist_id[0]
        if self.pricelist_id2:
            price_context['pricelist2'] = self.pricelist_id2[0]
        prods = self.pool['product.product'].browse(self.cr, self.uid, prod_ids, context=price_context)
        return prods
        
    def _getProducts(self, category, lang):
        prod_tmpIDs = self.pool['product.template'].search(self.cr, self.uid, [('categ_id', '=', category)])
        prod_ids = self.pool['product.product'].search(self.cr, self.uid, [('product_tmpl_id', 'in', prod_tmpIDs)])
        prods = self.pool['product.product'].browse(self.cr, self.uid, prod_ids, context={'lang': lang})
        return prods
    
    def get_pricelist(self, a):
        result = []
        pooler.get_pool(self.cr.dbname).get('product.pricelist')
        self.pricelist = a.get('pricelist_id', False)
        return result


report_sxw.report_sxw('report.product.catalog.extend', 'product.product', 'addons/product_catalog_extend/report/product_catalog_report.rml', parser=product_catalog_report, header=0)
report_sxw.report_sxw('report.product.catalog.extend2', 'product.product', 'addons/product_catalog_extend/report/product_catalog_report2.rml', parser=product_catalog_report, header=0)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
