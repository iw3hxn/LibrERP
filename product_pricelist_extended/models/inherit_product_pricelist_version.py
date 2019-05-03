# -*- coding: utf-8 -*-
# © 2018 Didotech srl (www.didotech.com)

import decimal_precision as dp
from openerp.osv import orm, fields
import time


class ProductPricelistVersion(orm.Model):
    _inherit = 'product.pricelist.version'

    def _pricelist_type_get(self, cr, uid, context=None):
        return self.pool['product.pricelist']._pricelist_type_get(cr, uid, context)

    def _product_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        context = context or self.pool['res.users'].context_get(cr, uid)
        quantity = 1.0
        product_id = context.get('product_id', False)
        if not product_id:
            for version_id in ids:
                res[version_id] = {
                    'price': 0.0,
                    'price_error': False,
                    'pricelist_rule_id': False,
                    'string_discount': '',
                    'row_color': 'black',
                    'price_uos': False,
                    # 'pricelist_rule_type': ''
                }
            return res

        partner = False
        product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
        date = time.strftime('%Y-%m-%d')
        new_ids = self.search(cr, uid, [('id', 'in', ids), '|', ('date_end', '=', False), ('date_end', '>=', date)], context=context)
        pricelist_versions = self.browse(cr, uid, new_ids, context)
        product_pricelist_obj = self.pool['product.pricelist']
        if product_id:
            cost_price = product.cost_price
            pricelist_ids = [pricelist_version.pricelist_id.id for pricelist_version in pricelist_versions]
            res_multi = product_pricelist_obj.price_rule_get_multi(cr, uid, pricelist_ids,
                                                               products_by_qty_by_partner=[
                                                                   (product, quantity, partner)],
                                                               context=context)[product_id]
        rule_ids = []
        for pricelist_version in self.browse(cr, uid, ids, context):
            res[pricelist_version.id] = {
                'price': 0.0,
                'price_uos': 0.0,
                'row_color': 'black',
                'pricelist_rule_id': False,
                'price_error': True,
                'string_discount': '',

                # 'pricelist_rule_type': ''
            }

            pricelist_id = pricelist_version.pricelist_id.id
            if pricelist_id in res_multi:
                res[pricelist_version.id]['price_error'] = False
                price, rule = res_multi[pricelist_id]
                uos_coeff = product.uos_coeff or 1
                res[pricelist_version.id].update({
                    'price': price,
                    'price_uos': price / uos_coeff
                })
                if price < cost_price:
                    res[pricelist_version.id]['row_color'] = 'red'
                if rule:
                    res[pricelist_version.id]['pricelist_rule_id'] = rule
                    rule_ids.append(rule)

        rules = self.pool['product.pricelist.item'].read(cr, uid, list(set(rule_ids)), ['string_discount'], context=context)
        for pricelist_version in pricelist_versions:
            if res[pricelist_version.id]['pricelist_rule_id']:
                res[pricelist_version.id]['string_discount'] = [p['string_discount'] for p in rules if p['id'] == res[pricelist_version.id]['pricelist_rule_id']][0]
        return res

    def _get_partner(self, cr, uid, ids, name, arg, context=None):
        return_res = {}
        context = context or {}
        product_pricelist_obj = self.pool['product.pricelist']

        for product_pricelist_version_id in ids:
            return_res[product_pricelist_version_id] = False
            product_pricelist_ids = product_pricelist_obj.search(cr, uid, [('version_id', '=', product_pricelist_version_id)], context=context)
            res = []
            for pricelist in product_pricelist_obj.read(cr, uid, product_pricelist_ids, ['partner_ids'], context=context):
                if pricelist['partner_ids']:
                    res += pricelist['partner_ids']

            # where_str = " WHERE " + \
            #             "name = '%s' AND " % 'property_product_pricelist' + \
            #             "res_id like '%s,%%' AND " % self.pool['res.partner']._name + \
            #             "company_id = %s AND " % cid + \
            #             "fields_id = %s AND " % def_id + \
            #             "type = '%s'" % self.pool['res.partner']._all_columns['property_product_pricelist'].column._type
            #
            # args1 = [('id', '=', product_pricelist_ids)]
            # model_obj = self.pool.get(property_field._obj)
            # model_ids = model_obj.search(cr, uid, args1, context=context)
            # if model_ids:
            #     model_ids = map(lambda x: "'%s,%s'" % (model_obj._name, x), model_ids)
            #     model_ids = ",".join(model_ids)
            #     where_str += ' AND value_reference IN (%s)' % model_ids
            #
            # query = "SELECT res_id FROM ir_property " + where_str
            # cr.execute(query)
            # res = cr.fetchall()
            # if res:
            #     res = set(res)
            #     res = map(lambda x: int(x[1]), [x[0].split(',') for x in res])
                return_res[product_pricelist_version_id] = list(set(res))

        return return_res



    _columns = {
        'type': fields.related('pricelist_id', 'type', type='selection', selection=_pricelist_type_get, string='Pricelist Type'),
        'price': fields.function(_product_price, type='float', string='Pricelist', method=True, multi='product_price',
                                 digits_compute=dp.get_precision('Sale Price')),
        'price_uos': fields.function(_product_price, type='float', string='Pricelist UoS', method=True, multi='product_price',
                                 digits_compute=dp.get_precision('Sale Price')),
        'pricelist_rule_id': fields.function(_product_price, obj='product.pricelist.item', type='many2one', string='Rule', method=True, multi='product_price'),
        # 'pricelist_rule_type': fields.function(_product_price, type='char', string='Rule type', method=True, multi='product_price'),
        'price_error': fields.function(_product_price, type='boolean', string='Pricelist Error', method=True, multi='product_price'),
        'string_discount': fields.function(_product_price, type='char', string='String Discount', size=20, multi='product_price'),
        'partner_id': fields.related('pricelist_id', 'partner_id', type='many2one', relation='res.partner',
                                     string='Partner'),
        'partner_ids': fields.function(_get_partner, string='Partners', type='one2many', relation="res.partner",
                                       readonly=True, method=True),
        'row_color': fields.function(_product_price, string='Row color', type='char', readonly=True,  multi='product_price', method=True),
    }

