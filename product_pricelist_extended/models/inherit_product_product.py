# -*- encoding: utf-8 -*-

import re

from openerp.osv import orm, fields


class product_product(orm.Model):

    _inherit = 'product.product'

    def _get_all_pricelist_ids(self, cr, uid, ids, field_name, arg, context):
        ret = {}
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

        return ret

    _columns = {
        'partner_pricelist_ids': fields.function(_get_all_pricelist_ids, method=True, type='many2many', relation='product.pricelist.version', string='Customer List Price', multi='_get_all_pricelist_ids'),
        'generic_pricelist_ids': fields.function(_get_all_pricelist_ids, method=True, type='many2many', relation='product.pricelist.version', string='Customer List Price',  multi='_get_all_pricelist_ids'),
    }
