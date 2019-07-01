# -*- coding: utf-8 -*-

from openerp.osv import orm, fields


class ProductLabel(orm.TransientModel):
    _name = "product.label"

    def _compute_selected(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context):
            if record.qty > 0:
                res[record.id] = True
            else:
                res[record.id] = False
        return res

    _columns = {
        'selected': fields.function(_compute_selected, string='Print', type='boolean'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'wizard_id': fields.many2one('print.product.label', 'Print Wizard'),
        'qty_initial': fields.integer('Initial Qty'),
        'qty': fields.integer('Label Qty'),
    }

    _defaults = {
        'qty_initial': 1,
        'qty': 1
    }

    def action_plus_qty(self, cr, uid, ids, context):
        for record in self.browse(cr, uid, ids, context):
            record.write({'qty': record.qty + 1})
        return True

    def action_minus_qty(self, cr, uid, ids, context):
        for record in self.browse(cr, uid, ids, context):
            if record.qty > 0:
                record.write({'qty': record.qty - 1})
        return True