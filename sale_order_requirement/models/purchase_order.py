# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from tools.translate import _


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def _get_customer_account_invoice_ids(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        has_group = self.pool['res.users'].has_group(cr, uid, 'account.group_customer_account_invoice')

        for po in self.browse(cr, uid, ids, context):
            account_invoice_ids = []
            if has_group:
                for order in po.sale_order_ids:
                    account_invoice_ids += [invoice.id for invoice in order.invoice_ids]

            result[po.id] = list(set(account_invoice_ids))
        return result

    _columns = {
        'sale_order_ids': fields.many2many('sale.order', string='Sale Orders', readonly=True),
        'customer_account_invoice_ids': fields.function(_get_customer_account_invoice_ids, string="Customer Invoice", type='one2many', method=True, relation='account.invoice'),
    }

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        product_supplierinfo_obj = self.pool['product.supplierinfo']
        product_uom = self.pool['product.uom']
        for po in self.browse(cr, uid, ids, context=context):
            partner_id = po.partner_id.id
            for line in po.order_line:
                qty = line.product_qty
                product = line.product_id
                supplierinfo_ids = product_supplierinfo_obj.search(cr, uid, [('name', '=', partner_id), ('product_id', '=', product.product_tmpl_id.id)])
                if supplierinfo_ids:
                    supplierinfo = product_supplierinfo_obj.browse(cr, uid, supplierinfo_ids[0], context=context)
                    uom_id = line.product_uom.id
                    min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                    if qty < min_qty:  # If the supplier quantity is greater than entered from user, set minimal.
                        raise orm.except_orm(_('Error'), _('The selected supplier has a minimal quantity set to {qty} for product "{product}"').format(qty=min_qty, product=product.name))

        return super(PurchaseOrder, self).wkf_confirm_order(cr, uid, ids, context=context)
