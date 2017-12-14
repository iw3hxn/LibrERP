# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from data_migration.utils.utils import Utils


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def get_create(self, cr, uid, values, context):
        product_ids = self.search(cr, uid, [('ean13', '=', values['Ean'])], context)
        if product_ids:
            return product_ids[0]
        else:
            product_values = self.default_get(cr, uid, (
                'taxes_id',
                'supplier_taxes_id',
                'cost_method',
                'uom_id',
                'uom_po_id'
            ), context)
            product_values.update({
                'name': values['Name'],
                'ean13': values['Ean'],
                'list_price': float(Utils.toStr(values['Price'])),

            })
            return self.create(cr, uid, product_values, context)
