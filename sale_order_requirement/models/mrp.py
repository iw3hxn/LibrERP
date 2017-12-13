# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from osv import osv, fields, orm
from datetime import datetime
from osv import osv, fields, orm
import decimal_precision as dp
from tools import float_compare
from tools import DEFAULT_SERVER_DATETIME_FORMAT
from tools.translate import _
import netsvc
import time
import tools

from operator import attrgetter

class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'

    def _child_compute_buy_and_produce(self, cr, uid, ids, name, arg, context=None):
        result = {}
        if context is None:
            context = {}
        bom_obj = self.pool.get('mrp.bom')
        bom_id = context and context.get('active_id', False) or False
        cr.execute('select id from mrp_bom')
        if all(bom_id != r[0] for r in cr.fetchall()):
            ids.sort()
            bom_id = ids[0]
        bom_parent = bom_obj.browse(cr, uid, bom_id, context=context)
        for bom in self.browse(cr, uid, ids, context=context):
            if bom_parent or (bom.id == bom_id):
                result[bom.id] = map(lambda x: x.id, bom.bom_lines)
            else:
                result[bom.id] = []
            if bom.bom_lines:
                continue
            ok = name == 'child_buy_and_produce_ids' and (bom.product_id.supply_method in ('buy', 'produce'))
            # Changed from inherited -> is GOOD ALSO bom.type=='buy',
            # it was -> and (bom.product_id.supply_method=='produce'))
            if bom.type == 'phantom' or ok:
                sids = bom_obj.search(cr, uid, [('bom_id', '=', False),
                                                ('product_id', '=', bom.product_id.id)])
                if sids:
                    bom2 = bom_obj.browse(cr, uid, sids[0], context=context)
                    result[bom.id] += map(lambda x: x.id, bom2.bom_lines)

        return result

    _columns = {
        'child_buy_and_produce_ids': fields.function(_child_compute_buy_and_produce, relation='mrp.bom',
                                                     string="BoM Hierarchy", type='many2many'),
    }


class mrp_production(osv.osv):

    _inherit = "mrp.production"

    _columns = {
        'is_from_order_requirement': fields.boolean(),
        'temp_bom_id': fields.many2one('temp.mrp.bom', 'Bill of Material', readonly=True),
        'level': fields.integer('Level', required=True)
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
        productions = self.browse(cr, uid, ids)
        if not productions:
            return 0
        if not productions[0].is_from_order_requirement:
            return super(mrp_production, self).action_compute(cr, uid, ids, properties, context)

        # If production order was created by order requirement, behaviour is different
        results = []
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
                raise osv.except_osv(_('Error'), _("Couldn't find a bill of material for this product."))
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            # Forcing routing_id to False, the lines are linked directly to temp_mrp_bom
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=False)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return len(results)
