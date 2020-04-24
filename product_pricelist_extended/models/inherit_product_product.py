# -*- encoding: utf-8 -*-

import decimal_precision as dp
from openerp.osv import orm, fields


class product_product(orm.Model):

    _inherit = 'product.product'

    def _get_all_pricelist_ids(self, cr, uid, ids, field_name, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        ret = {}
        if context.get('show_listprice', False):
            partner_name = context.get('partner_name', False)
            if partner_name:
                partner_obj = self.pool['res.partner']
                partner_ids = partner_obj.search(cr, uid, [('name', '=', partner_name)], context=context)
                pricelist_customer_version_ids = []
                pricelist_version_ids = []
                if partner_ids:
                    partner = partner_obj.browse(cr, uid, partner_ids[0], context=context)
                    product_pricelist_id = partner.property_product_pricelist and partner.property_product_pricelist.id or False
                    pricelist_customer_version_ids = self.pool['product.pricelist.version'].search(cr, uid, [('pricelist_id', '=', product_pricelist_id)], context=context)
                    cr.execute(
                        " SELECT sale_shop.pricelist_id FROM sale_shop GROUP BY pricelist_id;"
                    )
                    pricelist_version_ids = self.pool['product.pricelist.version'].search(cr, uid, [('pricelist_id', 'in', [pricelist_version_id[0] for pricelist_version_id in cr.fetchall()])], context=context)
            else:
                cr.execute(
                    " SELECT product_pricelist_version.id " \
                    " FROM " \
                    "  product_pricelist, " \
                    "  product_pricelist_version, " \
                    "  res_partner " \
                    " WHERE " \
                    "  product_pricelist.partner_id = res_partner.id AND " \
                    "  product_pricelist_version.pricelist_id = product_pricelist.id AND " \
                    "  product_pricelist.type = 'sale' AND " \
                    "  product_pricelist.partner_id IS NOT NULL  AND " \
                    "  product_pricelist.active IS TRUE AND " \
                    "  product_pricelist_version.active IS TRUE " \
                    " ORDER BY" \
                    "  res_partner.name ASC;"
                )
                pricelist_customer_version_ids = [pricelist_version_id[0] for pricelist_version_id in cr.fetchall()]

                cr.execute(
                    " SELECT product_pricelist_version.id " \
                    " FROM " \
                    "  product_pricelist, " \
                    "  product_pricelist_version " \
                    " WHERE " \
                    "  product_pricelist_version.pricelist_id = product_pricelist.id AND " \
                    "  product_pricelist.type = 'sale' AND " \
                    "  product_pricelist.partner_id IS NULL  AND " \
                    "  product_pricelist.active IS TRUE AND " \
                    "  product_pricelist_version.active IS TRUE " \
                    " ORDER BY" \
                    "  product_pricelist.name ASC;"
                )
                pricelist_version_ids = [pricelist_version_id[0] for pricelist_version_id in cr.fetchall()]

            for product_id in ids:
                ret[product_id] = {
                    'partner_pricelist_ids': pricelist_customer_version_ids,
                    'generic_pricelist_ids': pricelist_version_ids
                }
        else:
            for product_id in ids:
                ret[product_id] = {
                    'partner_pricelist_ids': [],
                    'generic_pricelist_ids': []
                }
            return ret

        return ret

    def _product_price_partner(self, cr, uid, ids, name, arg, context=None):
        # if context is None:
        #     context = {}
        # res = super(product_product, self)._product_price(cr, uid, ids, name, arg, context)
        context = context or self.pool['res.users'].context_get(cr, uid)
        partner_name = context.get('partner_name', False)
        if partner_name:
            partner_obj = self.pool['res.partner']
            partner_ids = partner_obj.search(cr, uid, [('name', '=', partner_name)], context=context)
            if partner_ids:
                partner = partner_obj.browse(cr, uid, partner_ids[0], context=context)
                context['pricelist'] = partner.property_product_pricelist and partner.property_product_pricelist.id or False
                context['partner'] = partner.id
            else:
                del context['partner_name']
                if 'pricelist' in context:
                    del context['pricelist']
        res = self.pool['product.product']._product_price(cr, uid, ids, name, arg, context)
        # res = {}
        # for id in ids:
        #     res.setdefault(id, 0.0)
        return res

    _columns = {
        'partner_id': fields.dummy(string='Customer', relation='res.partner', type='many2one',
                                   domain=[('customer', '=', True)]),
        'price': fields.function(_product_price_partner, type='float', string='Pricelist', digits_compute=dp.get_precision('Sale Price')),
        'partner_pricelist_ids': fields.function(_get_all_pricelist_ids, method=True, type='many2many', relation='product.pricelist.version', string='Customer List Price', multi='_get_all_pricelist_ids'),
        'generic_pricelist_ids': fields.function(_get_all_pricelist_ids, method=True, type='many2many', relation='product.pricelist.version', string='Customer List Price',  multi='_get_all_pricelist_ids'),
    }
