# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from tools.translate import _


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    _columns = {
        'sale_order_ids': fields.many2many('sale.order', string='Sale Orders', readonly=True),
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

        return super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)


class procurement_order(orm.Model):
    _inherit = 'procurement.order'

    def action_po_assign(self, cr, uid, ids, context=None):
        """ This is action which call from workflow to assign purchase order to procurements
        @return: True
        """
        return 0

