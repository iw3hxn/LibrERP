# -*- coding: utf-8 -*-

from osv import orm, fields


class SaleOrderLine(orm.Model):
    _inherit = "sale.order.line"

    _columns = {
        # 'sale_order_date': fields.related('order_id', 'order_date', string='Date', type='date'),
        'product_sale_order_history_id': fields.many2one('sale.order.line', 'Parent Order', select=True),
        'product_sale_order_history_ids': fields.one2many('sale.order.line', 'product_sale_order_history_id', string='Order History'),
    }

    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
                          flag=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(SaleOrderLine, self).product_id_change(cr, uid, ids, pricelist, product_id, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        if (product_id and partner_id) and not context.get('pos_order_type', False):
            product_sell_ids = self.search(cr, uid, [('product_id', '=', product_id), ('order_partner_id', '!=', partner_id)], context=context)
            partner_sell_ids = self.search(cr, uid, [('product_id', '=', product_id), ('order_partner_id', '=', partner_id)], context=context)
            res['value']['product_sale_order_history_ids'] = partner_sell_ids + product_sell_ids
        return res
