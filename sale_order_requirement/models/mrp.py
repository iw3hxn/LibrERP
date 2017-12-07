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

    def _bom_find(self, cr, uid, product_id, product_uom, properties=[], is_from_order_requirement=False):
        """ Finds BoM for particular product and product uom.
        @param product_id: Selected product.
        @param product_uom: Unit of measure of a product.
        @param properties: List of related properties.
        @return: False or BoM id.
        If Production order was created by order requirement, it will use temp.mrp.bom instead of mrp.bom
        """
        if not is_from_order_requirement:
            return super(mrp_bom, self)._bom_find(cr, uid, product_id, product_uom, properties)

        domain = [('product_id', '=', product_id), ('bom_id', '=', False),
                  '|', ('date_start', '=', False), ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                  '|', ('date_stop', '=', False), ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
        ids = self.search(cr, uid, domain, order='sequence')
        max_prop = 0
        result = False
        for bom in self.pool.get('mrp.bom').browse(cr, uid, ids):
            prop = 0
            for prop_id in bom.property_ids:
                if prop_id.id in properties:
                    prop += 1
            if (prop > max_prop) or ((max_prop == 0) and not result):
                result = bom.id
                max_prop = prop
        return result

    def _bom_explode(self, cr, uid, bom, factor, properties=[], addthis=False, level=0, routing_id=False):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product.
        @param factor: Factor of product UoM.
        @param properties: A List of properties Ids.
        @param addthis: If BoM found then True else False.
        @param level: Depth level to find BoM lines starts from 10.
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        routing_obj = self.pool.get('mrp.routing')
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_lines:
            newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)

            if newbom:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor * bom.product_qty,
                                        properties, addthis=True, level=level + 10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        if not phantom:
            if addthis and not bom.bom_lines:
                result.append(
                    {
                        'name': bom.product_id.name,
                        'product_id': bom.product_id.id,
                        'product_qty': bom.product_qty * factor,
                        'product_uom': bom.product_uom.id,
                        'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                        'product_uos': bom.product_uos and bom.product_uos.id or False,
                    })
            routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
            if routing:
                for wc_use in routing.workcenter_lines:
                    wc = wc_use.workcenter_id
                    d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                    mult = (d + (m and 1.0 or 0.0))
                    cycle = mult * wc_use.cycle_nbr
                    result2.append({
                        'name': tools.ustr(wc_use.name) + ' - ' + tools.ustr(bom.product_id.name),
                        'workcenter_id': wc.id,
                        'sequence': level + (wc_use.sequence or 0),
                        'cycle': cycle,
                        'hour': float(wc_use.hour_nbr * mult + (
                                (wc.time_start or 0.0) + (wc.time_stop or 0.0) + cycle * (wc.time_cycle or 0.0)) * (
                                              wc.time_efficiency or 1.0)),
                    })
            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level + 10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2

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
        'is_from_order_requirement': fields.boolean()
    }

    _defaults = {
        'is_from_order_requirement': False
    }

    def action_compute(self, cr, uid, ids, properties=[], context=None):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        If necessary, redirects to temp.mrp.bom instead of mrp.bom
        """

        productions = self.browse(cr, uid, ids)
        if not productions:
            return 0
        if not productions[0].is_from_order_requirement:
            return super(mrp_production, self).action_compute(cr, uid, ids, properties, context)

        # If production order was created by order requirement, behaviour is different
        results = []
        bom_obj = self.pool['mrp.bom']
        uom_obj = self.pool['product.uom']
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool['mrp.production.workcenter.line']
        for production in self.browse(cr, uid, ids):
            cr.execute('delete from mrp_production_product_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_production_workcenter_line where production_id=%s', (production.id,))
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties, True)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise osv.except_osv(_('Error'), _("Couldn't find a bill of material for this product."))
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id.id)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return len(results)

    def action_confirm000(self, cr, uid, ids, context=None):
        """ Confirms production order.
        @return: Newly generated Shipment Id.
        """
        shipment_id = False
        wf_service = netsvc.LocalService("workflow")
        uncompute_ids = filter(lambda x: x, [not x.product_lines and x.id or False for x in
                                             self.browse(cr, uid, ids, context=context)])

        # TODO: Serve? Anche se commentato, viene eseguita grazie a workflow ->
        # self.action_compute(cr, uid, uncompute_ids, context=context)

        for production in self.browse(cr, uid, ids, context=context):

            shipment_id = production.picking_id.id

            wf_service.trg_validate(uid, 'stock.picking', shipment_id, 'button_confirm', cr)
            production.write({'state': 'confirmed'}, context=context)
            message = _("Manufacturing order '%s' is scheduled for the %s.") % (
                production.name,
                datetime.strptime(production.date_planned, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
            )
            self.log(cr, uid, production.id, message)
        return shipment_id

    def action_compute000(self, cr, uid, ids, properties=[], context=None):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        # TODO MUST change from mrp.bom to temp.mrp.bom and from routing_id to temp_routing?
        # TODO return 0 for avoiding creation of "Prodotti programmati"
        return 0

        results = []
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids):
            cr.execute('delete from mrp_production_product_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_production_workcenter_line where production_id=%s', (production.id,))
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise osv.except_osv(_('Error'), _("Couldn't find a bill of material for this product."))
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id.id)
            results = res[0]
            results2 = res[1]
            for line in results:
                # TODO => This will create "Prodotti programmati"
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)

            for line in results2:
                # TODO -=> DON'T create, we already have it in _manufacture_bom
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return len(results)
