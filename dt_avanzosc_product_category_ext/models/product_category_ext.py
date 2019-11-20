
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp.osv import orm, fields
#
### HEREDO LA PRODUCTOS PARA AÑADIRLE CAMPOS NUEVOS
#


class product_category(orm.Model):
    
    _name = 'product.category'
    _inherit = 'product.category'
    
    def _manage_tax_on_category(self, cr, uid, ids, field_name, arg, context):
        res = {}
        company_id = self.pool['res.users'].browse(cr, uid, uid, context).company_id.id
        company_obj = self.pool['res.company']
        company = company_obj.browse(cr, uid, company_id, context)
        
        for product_id in ids:
            res[product_id] = company.manage_tax_on_category
        return res
    
    _columns = {
        'provision_type': fields.selection([('product', 'Stockable Product'), ('consu', 'Consumable'), ('service', 'Service')], 'Product Type', help="Will change the way procurements are processed. Consumable are product where you don't manage stock."),
        'procure_method': fields.selection([('make_to_stock', 'Make to Stock'), ('make_to_order', 'Make to Order')], 'Procurement Method', help="'Make to Stock': When needed, take from the stock or wait until re-supplying. 'Make to Order': When needed, purchase or produce for the procurement request."),
        'supply_method': fields.selection([('produce', 'Produce'), ('buy', 'Buy')], 'Supply method', help="Produce will generate production order or tasks, according to the product type. Buy will trigger purchase orders when requested."),
        'sale_taxes_ids': fields.many2many('account.tax', 'product_cat_tax_cust_rel', 'cat_id', 'tax_id', 'Sale Taxes', domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['sale', 'all'])], help='Taxes applied on sale orders'),
        'purchase_taxes_ids': fields.many2many('account.tax', 'product_cat_tax_supp_rel', 'cat_id', 'tax_id', 'Purchase Taxes', domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['purchase', 'all'])], help='Taxes applied on purchase orders'),
        'uom_id': fields.many2one('product.uom', 'Default UoM', help='Default Unit of Measure'),
        'uom_po_id': fields.many2one('product.uom', 'Purchase UoM', help='Unit of Measure for purchase'),
        'uos_id': fields.many2one('product.uom', 'Unit of Sale', help='See product definition'),
        'uos_coef': fields.float('UOM -> UOS coef', digits=(16, 4), help='See product definition'),
        'manage_tax_on_category': fields.function(_manage_tax_on_category, string="Manage Tax on category", type='boolean', readonly=True, method=True),
    }
