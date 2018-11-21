# -*- coding: utf-8 -*-

from osv import orm, fields


class PurchaseOrderLine(orm.Model):
    _inherit = "purchase.order.line"

    _columns = {
      #  'sale_order_date': fields.related('order_id', 'order_date', 'Date', type='date'),
        'product_purchase_order_history_id': fields.many2one('purchase.order.line', 'Parent Order', select=True),
        'product_purchase_order_history_ids': fields.one2many('purchase.order.line', 'product_purchase_order_history_id', string='Order History'),
    }

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, notes=False, context=None):

        context = context or self.pool['res.users'].context_get(cr, uid)

        res = super(PurchaseOrderLine, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                                                                   partner_id, date_order, fiscal_position_id,
                                                                   date_planned,
                                                                   name, price_unit, notes, context)
        if product_id and partner_id:
            product_sell_ids = self.search(cr, uid, [('product_id', '=', product_id), ('partner_id', '!=', partner_id), ('state', '!=', 'draft')], context=context)
            partner_sell_ids = self.search(cr, uid, [('product_id', '=', product_id), ('partner_id', '=', partner_id), ('state', '!=', 'draft')], context=context)

            res['value']['product_purchase_order_history_ids'] = partner_sell_ids + product_sell_ids
        return res
