# -*- coding: utf-8 -*-
# © 2018 Didotech srl (www.didotech.com)

import decimal_precision as dp
from openerp.osv import orm, fields


class ProductPricelistItem(orm.TransientModel):
    _name = 'wizard.product.pricelist.item'

    def _price_field_get(self, cr, uid, context=None):
        return self.pool['product.pricelist.item']._price_field_get(cr, uid, context)

    def _get_default_base(self, cr, uid, fields, context=None):
        product_price_type_obj = self.pool.get('product.price.type')
        if fields.get('type') == 'purchase':
            product_price_type_ids = product_price_type_obj.search(cr, uid, [('field', '=', 'standard_price')], context=context)
        elif fields.get('type') == 'sale':
            product_price_type_ids = product_price_type_obj.search(cr, uid, [('field', '=', 'list_price')], context=context)
        else:
            return -1
        if not product_price_type_ids:
            return False
        else:
            pricetype = product_price_type_obj.browse(cr, uid, product_price_type_ids, context=context)[0]
            return pricetype.id

    _defaults = {
        'base': _get_default_base,
        'min_quantity': lambda *a: 0,
        'sequence': lambda *a: 5,
        'price_discount': lambda *a: 0,
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        for obj_list in self.browse(cr, uid, ids, context=context):
            if obj_list.base == -1:
                main_pricelist = obj_list.price_version_id.pricelist_id.id
                other_pricelist = obj_list.base_pricelist_id.id
                if main_pricelist == other_pricelist:
                    return False
        return True

    _columns = {
        'name': fields.char('Rule Name', size=64, help="Explicit rule name for this pricelist line."),
        'product_tmpl_id': fields.many2one('product.template', 'Product Template', ondelete='cascade',
                                           help="Set a template if this rule only apply to a template of product. Keep empty for all products"),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade',
                                      help="Set a product if this rule only apply to one product. Keep empty for all products"),
        'categ_id': fields.many2one('product.category', 'Product Category', ondelete='cascade',
                                    help="Set a category of product if this rule only apply to products of a category and his children. Keep empty for all products"),

        'min_quantity': fields.integer('Min. Quantity', required=True,
                                       help="The rule only applies if the partner buys/sells more than this quantity."),
        'sequence': fields.integer('Sequence', required=True,
                                   help="Gives the order in which the pricelist items will be checked. The evaluation gives highest priority to lowest sequence and stops as soon as a matching item is found."),
        'base': fields.selection(_price_field_get, 'Based on', required=True, size=-1,
                                 help="The mode for computing the price for this rule."),
        'base_pricelist_id': fields.many2one('product.pricelist', 'If Other Pricelist'),

        'price_surcharge': fields.float('Price Surcharge',
                                        digits_compute=dp.get_precision('Sale Price')),
        'price_discount': fields.float('Price Discount', digits=(16, 4)),
        'price_round': fields.float('Price Rounding',
                                    digits_compute=dp.get_precision('Sale Price'),
                                    help="Sets the price so that it is a multiple of this value.\n" \
                                         "Rounding is applied after the discount and before the surcharge.\n" \
                                         "To have prices that end in 9.99, set rounding 10, surcharge -0.01" \
                                    ),
        'price_min_margin': fields.float('Min. Price Margin',
                                         digits_compute=dp.get_precision('Sale Price')),
        'price_max_margin': fields.float('Max. Price Margin',
                                         digits_compute=dp.get_precision('Sale Price')),
        'pricelist_ids': fields.many2many('product.pricelist', string='Price List')
    }

    _constraints = [
        (_check_recursion, 'Error ! You cannot assign the Main Pricelist as Other Pricelist in PriceList Item!',
         ['base_pricelist_id'])
    ]

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code', 'name'], context=context)
        if prod[0]['code']:
            return {'value': {'name': prod[0]['code']}}
        return {}

    def add_rule(self, cr, uid, ids, context=None):
        self.fields_get(cr, uid, context=context)
        wizard = self.read(cr, uid, ids[0], self.fields_get(cr, uid, context=context).keys(), context=context)
        rule_value = wizard.copy()
        del rule_value['pricelist_ids']
        if rule_value.get('product_id', False):
            rule_value['product_id'] = rule_value['product_id'][0]
        if rule_value.get('product_tmpl_id', False):
            rule_value['product_tmpl_id'] = rule_value['product_tmpl_id'][0]
        if rule_value.get('categ_id', False):
            rule_value['categ_id'] = rule_value['categ_id'][0]
        if rule_value.get('base_pricelist_id', False):
            rule_value['base_pricelist_id'] = rule_value['base_pricelist_id'][0]

        for pricelist_id in wizard['pricelist_ids']:
            version_ids = self.pool['product.pricelist'].read(cr, uid, pricelist_id, ['version_id'], context=context)['version_id']
            if version_ids:
                version_id = version_ids[0]
                rule_value['price_version_id'] = version_id
                self.pool['product.pricelist.item'].create(cr, uid, rule_value,context)
        return {'type': 'ir.actions.act_window_close'}
