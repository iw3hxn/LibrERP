# -*- coding: utf-8 -*-

from openerp.osv import orm, fields

from openerp.tools.translate import _

TEMPLATE = [
            ('garazd_product_label.report_product_label_70x36_template', 'Label 70x36mm (A4: 21 pcs on sheet, 3x7)')]


class PrintProductLabel(orm.TransientModel):
    _name = "print.product.label"

    def _get_products(self, cr, uid, context):
        res = []
        if context.get('active_model') == 'product.template':
            products = self.pool[context.get('active_model')].browse(cr, uid, context.get('default_product_ids'), context)
            for product in products:
                label_id = self.pool['product.label'].create(cr, uid, {
                    'product_id': product.id,
                }, context)
                res.append(label_id)
        elif context.get('active_model') == 'product.product':
            products = self.pool[context.get('active_model')].browse(cr, uid, context.get('default_product_ids'), context)
            for product in products:
                label_id = self.pool['product.label'].create(cr, uid, {
                    'product_id': product.id,
                }, context)
                res.append(label_id)
        return res

    _columns = {
        'name': fields.char('Name'),
        'label_ids': fields.one2many('product.label', 'wizard_id', string='Labels for Products'),
        'template': fields.selection(TEMPLATE, string='Label template'),
        'qty_per_product': fields.integer('Label quantity per product'),
    }

    _defaults = {
        'name': _('Print Product Labels'),
        'label_ids': _get_products,
        'template': 'garazd_product_label.report_product_label_70x36_template',
        'qty_per_product': 1
    }

    def action_print(self, cr, uid, ids, context):
        # labels = self.label_ids.filtered('selected').mapped('id')
        # if not labels:
        #     raise Warning(_('Nothing to print, set the quantity of labels in the table.'))

        wizard = self.browse(cr, uid, ids[0], context)
        ctx = {}
        return self.pool['account.invoice'].print_report(cr, uid, ids, wizard.template, ctx)

    def action_set_qty(self, cr, uid, ids, context):
        wizard = self.browse(cr, uid, ids[0], context)
        label_ids = wizard.label_ids
        for label in label_ids:
            label.write({'qty': wizard.qty_per_product})
        return True

    def action_restore_initial_qty(self, cr, uid, ids, context):
        label_ids = self.browse(cr, uid, ids[0], context).label_ids

        for label in label_ids:
            if label.qty_initial:
                label.write({'qty': label.qty_initial})
        return True
