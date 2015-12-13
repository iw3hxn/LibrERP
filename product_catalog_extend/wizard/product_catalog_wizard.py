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
from openerp.osv import orm, fields


class product_catalog_wizard(orm.TransientModel):
    _name = 'product.catalog.wizard'
    _description = '#print Product Catalog Report'

    _columns = {
        'name': fields.char('Name', size=128, required=False, readonly=True),
        'category_id': fields.many2one('product.category', 'Category Type', ),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist 1'),
        'pricelist_id2': fields.many2one('product.pricelist', 'Pricelist 2'),
    }
    
    _defaults = {
        'pricelist_id': 1,
        'pricelist_id2': 0,
        'name': 'Report',
    }

    def print_report(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}

        res = self.read(cr, uid, ids, ['category_id', 'pricelist_id', 'pricelist_id2'], context=context)

        res = res and res[0] or {}

        datas['form'] = res
        datas['form']['ids'] = context.get('active_ids', [])
        report_name = res['pricelist_id2'] and 'product.catalog.extend2' or 'product.catalog.extend'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
        }
