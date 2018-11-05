# -*- coding: utf-8 -*-
# © 2017-2018 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from data_migration.utils.utils import Utils


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def get_create(self, cr, uid, values, context):
        if len(values['Ean']) == 13 and values['Ean'].isdigit():
            product_ids = self.search(cr, uid, [('ean13', '=', values['Ean'])], context=context)
        else:
            product_ids = self.search(cr, uid, [('default_code', '=', values['Ean'])], context=context)

        if product_ids:
            return product_ids[0]
        else:
            product_values = self.pool['product.template'].default_get(cr, uid, (
                'taxes_id',
                'supplier_taxes_id',
                'cost_method',
                'uom_id',
                'uom_po_id',
                'property_account_income',
                'property_account_expense',
                'supplier_taxes_id'
            ), context)

            product_values.update({
                'name': values['Name'],
                'ean13': len(values['Ean']) == 13 and values['Ean'] or '',
                'default_code': values['Ean'],
                'list_price': float(Utils.toStr(values['Price'])),
                'procure_method': 'make_to_order'
            })
            if product_values.get('taxes_id', False):
                product_values['taxes_id'] = [(6, 0, product_values.get('taxes_id'))]

            if product_values.get('supplier_taxes_id', False):
                product_values['supplier_taxes_id'] = [(6, 0, product_values.get('supplier_taxes_id'))]

            if product_values.get('property_account_income_categ', False):
                product_values['property_account_income_categ'] = self.pool['product.category'].default_get(cr, uid, ['property_account_income_categ'])

            if product_values.get('property_account_expense', False):
                product_values['property_account_expense'] = self.pool['product.category'].default_get(cr, uid, ['property_account_expense'])

            return self.create(cr, uid, product_values, context)
