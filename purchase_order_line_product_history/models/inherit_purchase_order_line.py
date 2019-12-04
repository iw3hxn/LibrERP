# -*- coding: utf-8 -*-

from osv import orm, fields


class PurchaseOrderLine(orm.Model):
    _inherit = "purchase.order.line"

    def _auto_init(self, cr, context={}):
        res = super(PurchaseOrderLine, self)._auto_init(cr, context)

        _index_name = 'purchase_order_line_product_id_index'
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s', (_index_name,))
        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON purchase_order_line (product_id)'.format(name=_index_name))

        _index_name = 'purchase_order_line_partner_id_index'
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s', (_index_name,))
        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON purchase_order_line (partner_id)'.format(name=_index_name))
        return res

    def _get_product_purchase_order_history_ids(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = self._get_connect_list(cr, uid, line.product_id.id, line.order_id.partner_id.id, line.order_id.date_order, context)
        return res

    _columns = {
        # 'sale_order_date': fields.related('order_id', 'order_date', 'Date', type='date'),
        # 'product_purchase_order_history_id': fields.many2one('purchase.order.line', 'Parent Order', select=True),
        'product_purchase_order_history_ids': fields.function(_get_product_purchase_order_history_ids, relation='purchase.order.line', type='one2many', string='Order History'),
    }

    def _get_connect_list(self, cr, uid, product_id, partner_id, date_order, context):
        res = []
        if product_id and partner_id:
            domain = [('product_id', '=', product_id), ('order_id.state', '!=', 'draft')]
            if date_order:
                domain.append(('order_id.date_order', '<', date_order))
            # product_sell_ids = self.search(cr, uid, [('product_id', '=', product_id), ('partner_id', '!=', partner_id), ('order_id.state', '!=', 'draft')], context=context)
            # partner_sell_ids = self.search(cr, uid, [('product_id', '=', product_id), ('partner_id', '=', partner_id), ('order_id.state', '!=', 'draft')], context=context)
            res = self.search(cr, uid, domain, context=context)
        return res

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, notes=False, context=None):

        context = context or self.pool['res.users'].context_get(cr, uid)

        res = super(PurchaseOrderLine, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                                                                 partner_id, date_order, fiscal_position_id,
                                                                 date_planned,
                                                                 name, price_unit, notes, context)

        res['value']['product_purchase_order_history_ids'] = self._get_connect_list(cr, uid, product_id, partner_id, False, context)

        return res

    def create(self, cr, uid, value, context):
        res = super(PurchaseOrderLine, self).create(cr, uid, value, context)
        return res
