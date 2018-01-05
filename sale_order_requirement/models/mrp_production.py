# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from osv import fields, orm
from tools.translate import _


class mrp_production(orm.Model):

    _inherit = "mrp.production"

    _columns = {
        'is_from_order_requirement': fields.boolean('is from order requirement'),
        'temp_bom_id': fields.many2one('temp.mrp.bom', 'Bill of Material', readonly=True),
        'level': fields.integer('Level', required=True),
        'sale_id': fields.many2one('sale.order', 'Sale order'),
    }

    _defaults = {
        'is_from_order_requirement': False,
        'level': 0
    }

    def action_compute(self, cr, uid, ids, properties=[], context=None):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        If necessary, redirects to temp.mrp.bom instead of mrp.bom
        """
        # action_compute is the Entry point for intercepting the mrp production
        productions = self.browse(cr, uid, ids, context)

        if not productions:
            return 0

        # NOTE: SINGLE PRODUCTION (not supported for multiple lines, problems with return len(results) )

        if not productions[0].is_from_order_requirement:
            return super(mrp_production, self).action_compute(cr, uid, ids, properties, context)

        results = []

        # If production order was created by order requirement, behaviour is different
        bom_obj = self.pool['temp.mrp.bom']
        uom_obj = self.pool['product.uom']
        prod_line_obj = self.pool['mrp.production.product.line']
        workcenter_line_obj = self.pool['mrp.production.workcenter.line']
        for production in self.browse(cr, uid, ids):
            cr.execute('delete from mrp_production_product_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_production_workcenter_line where production_id=%s', (production.id,))

            bom_point = production.temp_bom_id
            bom_id = production.temp_bom_id.id

            if not (bom_point or bom_id):
                raise orm.except_orm(_('Error'), _("Couldn't find a bill of material for this product."))
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            # Forcing routing_id to False, the lines are linked directly to temp_mrp_bom
            res = bom_obj._temp_mrp_bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, context)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return len(results)

    # def write(self, cr, uid, ids, values, context):
    #     if 'product_lines' in values:
    #         production_product_obj = self.pool['mrp.production.product.line']
    #         for line in values['product_lines']:
    #             if line[0] == 0:
    #                 message = _(u"Added Product: '{}', quantity: {}").format(
    #                     line[2]['name'], line[2]['product_qty'])
    #                 title = 'Added'
    #             elif line[0] == 1:
    #                 bom_line = production_product_obj.browse(cr, uid, line[1], context)
    #                 updated = ["{}: {} -> {}".format(key, getattr(bom_line, key, ''), value) for key, value in line[2].items()]
    #                 message = _(u"Updated Product: '{}': {}").format(bom_line.product_id.default_code,
    #                                                                  ', '.join(updated))
    #                 title = 'Updated'
    #             elif line[0] == 2:
    #                 bom_line = production_product_obj.browse(cr, uid, line[1], context)
    #                 message = _(u"Deleted Product: '{}'").format(bom_line.product_id.default_code)
    #                 title = 'Deleted'
    #             else:
    #                 message = False
    #             if message:
    #                 for bom_id in ids:
    #                     self.message_append(cr, uid, [bom_id], message, body_text=message, context=context)
    #                     # self.mail_post(cr, uid, bom_id, message, title, context)
    #     return super(mrp_production, self).write(cr, uid, ids, values, context)