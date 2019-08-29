# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class MrpBom(orm.Model):
    
    _inherit = "mrp.bom"

    def _get_color(self, cr, uid, ids, field_name, arg, context):
        res = {}

        product_obsolete_ids = self.pool['product.product'].search(cr, uid, [('state', 'in', ('draft', 'end', 'obsolete'))], context=context)
        for line in self.read(cr, uid, ids, ['product_id'], context=context, load='_obj'):
            if line['product_id'] in product_obsolete_ids:
                res[line['id']] = 'blue'
            else:
                res[line['id']] = 'black'
        return res

    _columns = {
        'row_color': fields.function(_get_color, string='Row color', type='char', readonly=True, method=True),
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

        return {'value': result.get('value', {}), 'warning': warning}
