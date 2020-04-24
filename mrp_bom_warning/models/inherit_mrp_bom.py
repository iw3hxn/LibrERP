# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class MrpBom(orm.Model):
    
    _inherit = "mrp.bom"

    @staticmethod
    def _get_color_product(qty):
        if qty > 0:
            return 'blue'
        return 'red'

    def _set_dummy(self, cr, uid, ids, name, value, arg, context=None):
        return True

    def _get_color(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid, context)

        res = {}

        mrp_bom_read = self.read(cr, uid, ids, ['product_id'], context=context, load='_obj')
        product_ids = list(set([line['product_id'] for line in mrp_bom_read]))

        product_obj = self.pool['product.product']
        product_obsolete_ids = product_obj.search(cr, uid, [('state', 'in', ('draft', 'end', 'obsolete'))], context=context)
        product_used_obsolete_ids = list(set(product_ids).intersection(product_obsolete_ids))
        product_obsolete = product_obj.read(cr, uid, product_used_obsolete_ids, ['qty_available'], context=context)
        product_obsolete_available = {}
        for product in product_obsolete:
            product_obsolete_available[product['id']] = product['qty_available']

        for line in mrp_bom_read:
            if line['product_id'] in product_used_obsolete_ids:
                res[line['id']] = self._get_color_product(product_obsolete_available[line['product_id']])
            else:
                res[line['id']] = 'black'
        return res

    _columns = {
        'row_color': fields.function(_get_color, fnct_inv=_set_dummy, string='Row color', type='char'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, name, context=None):
        result = super(MrpBom, self).onchange_product_id(cr, uid, ids, product_id, name, context)
        
        if not product_id:
            return result

        warning = {}
        product_obj = self.pool['product.product']
        product_info = product_obj.browse(cr, uid, product_id, context)
        title = False
        message = False

        if product_info.mrp_bom_warn != 'no-message':
            if product_info.mrp_bom_warn == 'block':
                raise orm.except_orm(_('Alert for %s !') % (product_info.name), product_info.mrp_bom_warn_msg)
            title = _("Warning for %s") % product_info.name
            message = product_info.mrp_bom_warn_msg
            warning['title'] = title
            warning['message'] = message

        if result.get('warning', False):
            warning['title'] = title and title + ' & ' + result['warning']['title'] or result['warning']['title']
            warning['message'] = message and message + '\n\n' + result['warning']['message'] or result['warning'][
                'message']

        # todo better code if write a single function
        if product_info.state in ['draft', 'end', 'obsolete']:
            result['value']['row_color'] = self._get_color_product(product_info.qty_available)

        return {'value': result.get('value', {}), 'warning': warning}
