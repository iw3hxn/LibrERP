# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Bortolatto Ivan. ( ivan.bortolatto(at)didotech.com )
#    Copyright (C) 2013 Didotech Inc. (<http://www.didotech.com>)
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
from osv import osv, fields


class product_catalog_available(osv.osv_memory):
    _name = 'product.catalog.available'
    _description = '#print Product Catalog Report with Qty Available'

    _columns = {
        'name': fields.char('Name', size = 128, required=False, readonly=True),
        'category_id': fields.many2one('product.category', 'Category Type', required=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist 1'),
        'pricelist_id2': fields.many2one('product.pricelist', 'Pricelist 2'),
    }
    
    _defaults = {
        'pricelist_id': 1,
        'pricelist_id2': 0,
    }

    def print_report_qty(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.browse(cr, uid, ids[0], context=context)
        # res = res and res[0] or {}
        datas['form'] = {}
        for key in ['category_id', 'pricelist_id', 'pricelist_id2']:
            datas['form'][key] = res[key] and res[key].id or False

        datas['form']['ids'] = context.get('active_ids', [])
        report_name = res['pricelist_id2'] and 'product.catalog.qty2' or 'product.catalog.qty'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
        }

product_catalog_available()
