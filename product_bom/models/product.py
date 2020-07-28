# -*- coding: utf-8 -*-
# © 2013-2018 Didotech srl (info@didotech.com)

import logging
import multiprocessing
import threading
import time
from datetime import datetime

import decimal_precision as dp
import pooler
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.config import config
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

ENABLE_CACHE = config.get('product_cache', False)
CACHE_TYPE = config.get('cache_type', 'dictionary')


class product_product(orm.Model):
    """
    Inherit Product in order to add an "Bom Stock" field
    """

    class UpdateCachePrice(threading.Thread):

        def __init__(self, cr, uid, product_product_obj, split_ids, context=None):
            self.cr = pooler.get_db(cr.dbname).cursor()
            self.product_product_obj = product_product_obj
            self.uid = uid
            self.context = context
            self.product_ids = split_ids

            threading.Thread.__init__(self)

        def run(self):
            try:
                time.sleep(5)
                for product in self.product_product_obj.browse(self.cr, self.uid, self.product_ids, self.context):
                    cost_price = product['cost_price']
                return True
            except Exception as e:
                # Rollback
                _logger.error(u'Error: {error}'.format(error=e))
                self.cr.rollback()
            finally:
                if not self.cr.closed:
                    self.cr.close()
            return True

        def terminate(self):
            if not self.cr.closed:
                self.cr.close()
            return True

    _inherit = 'product.product'
    
    # def _get_prefered_supplier(self, cr, uid, ids, field_name, args, context):
    #     res = {}
    #     for line in self.browse(cr, uid, ids, context):
    #         res[line.id] = line.seller_ids and line.seller_ids[0].name.id or False
    #     return res

    def __init__(self, cr, uid):
        super(product_product, self).__init__(cr, uid)

        if CACHE_TYPE == 'redis':
            try:
                from openerp.addons.core_extended.redis import Redis
                host = config.get('redis_host', 'localhost')

                self.product_cost_cache = Redis(host, database=cr.db_name, model=self._name)
            except:
                _logger.error("Unable to import Redis")
                from openerp.addons.core_extended.dict_cache import SimpleCache
                self.product_cost_cache = SimpleCache()
        else:
            from openerp.addons.core_extended.dict_cache import SimpleCache
            self.product_cost_cache = SimpleCache()

    def _hook_compute_purchase_price_no_supplier(self, product):
        return product.standard_price

    def product_cache(func):
        def cached_product(self, cr, uid, product, bom_properties, context=None):
            if product.id in self.product_cost_cache and not context.get('partner_name', False):
                _logger.debug('Returning from cache')
                return self.product_cost_cache[product.id]
            else:
                value = func(self, cr, uid, product, bom_properties, context=context)
                self.product_cost_cache[product.id] = value
                return value

        if ENABLE_CACHE:
            return cached_product
        else:
            return func

    @product_cache
    def _get_subproduct_cost_price(self, cr, uid, product, bom_properties, context=None):
        return product.cost_price

    @product_cache
    def _compute_product_purchase_price(self, cr, uid, product, bom_properties, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        bom_properties = bom_properties or []
        user = self.pool['res.users'].browse(cr, uid, uid, context)

        bom_obj = self.pool['mrp.bom']
        uom_obj = self.pool['product.uom']

        debug_logger = True

        if ENABLE_CACHE:
            if debug_logger:
                _logger.debug(u'[{product.default_code}] {product.name}'.format(product=product))
            # cached_price = self.product_cost_cache.get(product_id, 0)

        bom_id = bom_obj._bom_find(cr, uid, product.id, product_uom=None, properties=bom_properties)
        if bom_id:
            sub_bom_ids = bom_obj.search(cr, uid, [('bom_id', '=', bom_id)], context=context)
            sub_products = bom_obj.browse(cr, uid, sub_bom_ids, context)

            price = 0.
            if ENABLE_CACHE and debug_logger:
                _logger.debug(
                    u'[{product.default_code}] Start Explosion ========================'.format(product=product))

            for sub_product in sub_products:
                if sub_product.product_id.id == product.id:
                    error = "Product '{product.name}' (id: {product.id}) is referenced to itself".format(
                        product=product)
                    _logger.error(error)
                    continue

                # std_price = sub_product.standard_price
                # if ENABLE_CACHE:
                #     if sub_product.product_id.id in self.product_cost_cache:
                #         std_price = self.product_cost_cache[sub_product.product_id.id]
                #     else:
                #         std_price = sub_product.product_id.cost_price
                #         self.product_cost_cache[sub_product.product_id.id] = std_price
                # else:
                #     std_price = sub_product.product_id.cost_price
                std_price = self._get_subproduct_cost_price(cr, uid, sub_product.product_id, False, context)

                qty = uom_obj._compute_qty(cr, uid,
                                           from_uom_id=sub_product.product_uom.id,
                                           qty=sub_product.product_qty,
                                           to_uom_id=sub_product.product_id.uom_po_id.id)
                if ENABLE_CACHE and debug_logger:
                    _logger.debug(
                        u'[{product.default_code}] price += {std_price} * {qty}'.format(product=sub_product.product_id,
                                                                                        std_price=std_price, qty=qty))

                # print(std_price, qty)
                price += std_price * qty

            if sub_products:
                # Don't use browse when we already have it
                bom = sub_products[0].bom_id
            else:
                bom = bom_obj.browse(cr, uid, bom_id, context)

            if bom.routing_id and not context.get('exclude_routing', False):
                for wline in bom.routing_id.workcenter_lines:
                    wc = wline.workcenter_id
                    cycle = wline.cycle_nbr
                    # hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) * (wc.time_efficiency or 1.0)
                    cost_efficiency = wline._get_cost_efficiency()[wline.id]
                    cost = (wc.costs_cycle * cycle + wc.costs_hour * (
                                wline.hour_nbr + (wc.time_start or 0.0) + (wc.time_stop or 0.0))) * (
                                       wc.time_efficiency or 1.0)
                    price += cost * cost_efficiency
            price /= bom.product_qty
            price = uom_obj._compute_price(cr, uid, bom.product_uom.id, price, bom.product_id.uom_id.id)
            if ENABLE_CACHE and debug_logger:
                _logger.debug(
                    u'==== SUM [{product.default_code}] bom_price = {price}'.format(product=product, price=price))

            return price
        else:
            # no BoM: use standard_price
            # use standard_price if no supplier indicated

            # if product_id in self.product_cost_cache and ENABLE_CACHE and not context.get('partner_name', False):
            #     return self.product_cost_cache[product_id]

            if product.prefered_supplier:
                pricelist = product.prefered_supplier.property_product_pricelist_purchase or False
                ctx = {
                    'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                }
                if context.get('partner_name', False):
                    partner_name = context.get('partner_name')
                    partner_ids = self.pool['res.partner'].search(cr, uid, [('name', '=', partner_name)],
                                                                  context=context)
                    partner_id = partner_ids[0]
                else:
                    partner_id = False
                if pricelist:
                    price, rule = self.pool['product.pricelist'].price_rule_get_multi(cr, uid, [pricelist.id], products_by_qty_by_partner=[(product, 1, partner_id)], context=context)[product.id][pricelist.id]
                else:
                    raise orm.except_orm(
                        _("Error"),
                        _("The supplier {supplier} have no pricelist associated").format(supplier=product.prefered_supplier.name))

                price_subtotal = 0.0
                if pricelist:
                    from_currency = pricelist.currency_id.id
                    to_currency = user.company_id.currency_id.id
                    price_subtotal = self.pool['res.currency'].compute(
                        cr, uid,
                        from_currency_id=from_currency,
                        to_currency_id=to_currency,
                        from_amount=price,
                        context=context
                    )
                cost_price = price_subtotal or price or product.standard_price
            else:
                cost_price = self._hook_compute_purchase_price_no_supplier(product)

            if ENABLE_CACHE and debug_logger:
                _logger.debug(
                    u'NO BOM [{product.default_code}] price = {price}'.format(product=product, price=cost_price))

            return cost_price

    def _compute_purchase_price_new(self, cr, uid, ids,
                                product_uom=None,
                                bom_properties=None,
                                context=None):
        '''
        Compute the purchase price, taking into account sub products and routing
        '''

        context = context or self.pool['res.users'].context_get(cr, uid)
        bom_properties = bom_properties or []

        res = {}
        debug_logger = True

        if not ids:
            ids = self.search(cr, uid, [])

        # workers = multiprocessing.cpu_count() / 2
        # with multiprocessing.Manager() as manager:
        #     return_funct_dict = manager.dict()
        #     threads = []
        #     for product_ids in self._chunkIt(ids, workers):
        #         if product_ids:
        #             thread = self.CreateProductCost(cr, uid, product_ids, bom_properties, context, return_funct_dict)
        #             thread.daemon = True
        #             thread.start()
        #             threads.append(thread)
        #     # wait for finish all multiprocessing created
        #     for job in threads:
        #         job.join()
        #     for return_funct_dict_key in return_funct_dict.keys():
        #         res[return_funct_dict_key] = return_funct_dict[return_funct_dict_key]

        # if debug_logger:
        for product in self.browse(cr, uid, ids, context):
            # res[product.id] = self._compute_product_purchase_price(cr, uid, product.id, bom_properties,
            #                                                        log_product=product, context=context)
            try:
                res[product.id] = self._compute_product_purchase_price(cr, uid, product, bom_properties, context=context)
            except Exception as e:
                res[product.id] = 99999999
                _logger.error(u'{product} ERRORE: {error}'.format(product=product.name_get()[0][1], error=e))

        # else:
        #     for product_id in ids:
        #         res[product_id] = self._compute_product_purchase_price(cr, uid, product_id, bom_properties, context=context)

        return res

    # def _compute_purchase_price(self, cr, uid, ids,
    #                             product_uom=None,
    #                             bom_properties=None,
    #                             context=None):
    #     '''
    #     Compute the purchase price, taking into account sub products and routing
    #     '''
    #
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     bom_properties = bom_properties or []
    #     user = self.pool['res.users'].browse(cr, uid, uid, context)
    #
    #     bom_obj = self.pool['mrp.bom']
    #     uom_obj = self.pool['product.uom']
    #
    #     res = {}
    #     ids = ids or []
    #
    #     for product in self.browse(cr, uid, ids, context):
    #         if ENABLE_CACHE:
    #             _logger.debug(u'[{product.default_code}] {product.name}'.format(product=product))
    #         bom_id = bom_obj._bom_find(cr, uid, product.id, product_uom=None, properties=bom_properties)
    #         if bom_id:
    #             sub_bom_ids = bom_obj.search(cr, uid, [('bom_id', '=', bom_id)], context=context)
    #             sub_products = bom_obj.browse(cr, uid, sub_bom_ids, context)
    #
    #             price = 0.
    #             if ENABLE_CACHE:
    #                 _logger.debug(u'[{product.default_code}] Start Explosion ========================'.format(product=product))
    #             for sub_product in sub_products:
    #                 if sub_product.product_id.id == product.id:
    #                     error = "Product '{product.name}' (id: {product.id}) is referenced to itself".format(product=product)
    #                     _logger.error(error)
    #                     continue
    #
    #                 # std_price = sub_product.standard_price
    #                 if ENABLE_CACHE:
    #                     if sub_product.product_id.id in self.product_cost_cache:
    #                         std_price = self.product_cost_cache[sub_product.product_id.id]
    #                     else:
    #                         std_price = sub_product.product_id.cost_price
    #                         self.product_cost_cache[sub_product.product_id.id] = std_price
    #                 else:
    #                     std_price = sub_product.product_id.cost_price
    #
    #                 qty = uom_obj._compute_qty(cr, uid,
    #                                            from_uom_id=sub_product.product_uom.id,
    #                                            qty=sub_product.product_qty,
    #                                            to_uom_id=sub_product.product_id.uom_po_id.id)
    #                 if ENABLE_CACHE:
    #                     _logger.debug(u'[{product.default_code}] price += {std_price} * {qty}'.format(product=sub_product.product_id, std_price=std_price, qty=qty))
    #
    #                 price += std_price * qty
    #                 # if sub_product.routing_id:
    #                 #     for wline in sub_product.routing_id.workcenter_lines:
    #                 #         wc = wline.workcenter_id
    #                 #         cycle = wline.cycle_nbr
    #                 #         # hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) * (wc.time_efficiency or 1.0)
    #                 #         price += wc.costs_cycle * cycle + wc.costs_hour * wline.hour_nbr
    #
    #             if sub_products:
    #                 # Don't use browse when we already have it
    #                 bom = sub_products[0].bom_id
    #             else:
    #                 bom = bom_obj.browse(cr, uid, bom_id, context)
    #
    #             if bom.routing_id and not context.get('exclude_routing', False):
    #                 for wline in bom.routing_id.workcenter_lines:
    #                     wc = wline.workcenter_id
    #                     cycle = wline.cycle_nbr
    #                     # hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) * (wc.time_efficiency or 1.0)
    #                     price += wc.costs_cycle * cycle + wc.costs_hour * wline.hour_nbr
    #             price /= bom.product_qty
    #             price = uom_obj._compute_price(cr, uid, bom.product_uom.id, price, bom.product_id.uom_id.id)
    #             if ENABLE_CACHE:
    #                 _logger.debug(
    #                     u'==== SUM [{product.default_code}] bom_price = {price}'.format(product=product, price=price))
    #             res[product.id] = price
    #         else:
    #             # no BoM: use standard_price
    #             # use standard_price if no supplier indicated
    #
    #             if product.id in self.product_cost_cache and ENABLE_CACHE and not context.get('partner_name', False):
    #                 res[product.id] = self.product_cost_cache[product.id]
    #                 continue
    #
    #             if product.prefered_supplier:
    #                 pricelist = product.prefered_supplier.property_product_pricelist_purchase or False
    #                 ctx = {
    #                     'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
    #                 }
    #                 if context.get('partner_name', False):
    #                     partner_name = context.get('partner_name')
    #                     partner_ids = self.pool['res.partner'].search(cr, uid, [('name', '=', partner_name)], context=context)
    #                     partner_id = partner_ids[0]
    #                 else:
    #                     partner_id = False
    #                 price = self.pool['product.pricelist'].price_get(cr, uid, [pricelist.id], product.id, 1, partner_id, context=ctx)[pricelist.id] or 0
    #
    #                 price_subtotal = 0.0
    #                 if pricelist:
    #                     from_currency = pricelist.currency_id.id
    #                     to_currency = user.company_id.currency_id.id
    #                     price_subtotal = self.pool['res.currency'].compute(
    #                         cr, uid,
    #                         from_currency_id=from_currency,
    #                         to_currency_id=to_currency,
    #                         from_amount=price,
    #                         context=context
    #                     )
    #                 cost_price = price_subtotal or price or product.standard_price
    #             else:
    #                 cost_price = self._hook_compute_purchase_price_no_supplier(product)
    #
    #             res[product.id] = cost_price
    #             if ENABLE_CACHE:
    #                 _logger.debug(
    #                     u'NO BOM [{product.default_code}] price = {price}'.format(product=product, price=cost_price))
    #
    #             if ENABLE_CACHE and not context.get('partner_name', False):
    #                 self.product_cost_cache[product.id] = res[product.id]
    #             continue
    #
    #     return res

    def get_cost_field(self, cr, uid, ids, context=None):
        start_time = datetime.now()
        context = context or self.pool['res.users'].context_get(cr, uid)
        end_time = datetime.now()
        duration_seconds = (end_time - start_time)
        duration = '{sec}'.format(sec=duration_seconds)
        _logger.info(u'get_cost_field get in {duration} for {id}'.format(duration=duration, id=ids))
        res = self._cost_price(cr, uid, ids, '', [], context)
        return res

    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        # _logger.error(
        #     u'START _cost_price for {ids} and {field}'.format(ids=ids, field=field_name))
        context = context or self.pool['res.users'].context_get(cr, uid)
        product_uom = context.get('product_uom')
        bom_properties = context.get('properties')
        company = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id
        ctx = context.copy()
        ctx.update({'exclude_routing': company.exclude_routing})

        # Set to False to use old function
        new = True

        if new:
            start_time = datetime.now()
            res = self._compute_purchase_price_new(cr, uid, ids, product_uom, bom_properties, context=ctx)
            end_time = datetime.now()
            duration_seconds = (end_time - start_time)
            duration = '{sec}'.format(sec=duration_seconds)
            _logger.info(u'_cost_price_new get in {duration} for {qty} products'.format(duration=duration, qty=len(ids)))
        # else:
        #     start_time = datetime.now()
        #     res = self._compute_purchase_price(cr, uid, ids, product_uom, bom_properties, context=ctx)
        #     end_time = datetime.now()
        #     duration_seconds = (end_time - start_time)
        #     duration = '{sec}'.format(sec=duration_seconds)
        #     _logger.info(u'_cost_price get in {duration} for {qty} products'.format(duration=duration, qty=len(ids)))

        return res

    def _kit_filter(self, cr, uid, obj, name, args, context):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if not args:
            return []
        bom_obj = self.pool['mrp.bom']
        for search in args:
            if search[0] == 'is_kit':
                bom_product_ids = []
                if search[2]:
                    bom_ids = bom_obj.search(cr, uid, [('bom_id', '=', False)], context=context)
                    if bom_ids:
                        bom_product_ids = self.search(cr, uid, [('bom_ids', 'in', bom_ids)], context=context)
                        # res = [bom.product_id.id for bom in bom_obj.browse(cr, uid, bom_ids, context)]
                if search[1] == '!=':
                    return [('id', 'not in', bom_product_ids)]
                return [('id', 'in', bom_product_ids)]
        return []

    def _is_kit(self, cr, uid, ids, product_uom=None, bom_properties=None, context=None):
        if not len(ids):
            return []
        '''
        Show if have or not a bom
        '''
        res = {}
        ids = ids or []
        for product_id in ids:
            # bom_id = bom_obj._bom_find(cr, uid, product.id, product_uom=None, properties=bom_properties)
            cr.execute("""SELECT id FROM mrp_bom WHERE product_id={product_id} and bom_id is null""".format(product_id=product_id))
            bom_id = cr.fetchall()
            if not bom_id:
                res[product_id] = False
            else:
                res[product_id] = True
        return res
    
    """
    Inherit Product in order to add an "Bom Stock" field
    """
    def _bom_stock_mapping(self, cr, uid, context=None):
        return {'real': 'qty_available',
                'virtual': 'virtual_available',
                'immediately': 'immediately_usable_qty'}

    # from profilehooks import profile
    # @profile(immediate=True)

    def _compute_bom_stock(self, cr, uid, product,
                           quantities, company, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        bom_obj = self.pool['mrp.bom']
        uom_obj = self.pool['product.uom']
        mapping = self._bom_stock_mapping(cr, uid, context=context)
        stock_field = mapping[company.ref_stock]

        product_qty = quantities.get(stock_field, 0.0)
        # find a bom on the product
        bom_id = bom_obj._bom_find(
            cr, uid, product.id, product.uom_id.id, properties=[])

        if bom_id:
            prod_min_quantities = []
            bom = bom_obj.browse(cr, uid, bom_id, context=context)
            if bom.bom_lines:
                stop_compute_bom = False
                # Compute stock qty of each product used in the BoM and
                # get the minimal number of items we can produce with them
                for line in bom.bom_lines:
                    prod_min_quantity = 0.0
                    bom_qty = line.product_id[stock_field] # expressed in product UOM
                    # the reference stock of the component must be greater
                    # than the quantity of components required to
                    # build the bom
                    line_product_qty = uom_obj._compute_qty_obj(cr, uid,
                                                                line.product_uom,
                                                                line.product_qty,
                                                                line.product_id.uom_id,
                                                                context=context)

                    if line_product_qty and (bom_qty > line_product_qty):
                        prod_min_quantity = bom_qty / line_product_qty  # line.product_qty is always > 0
                    else:
                        # if one product has not enough stock,
                        # we do not need to compute next lines
                        # because the final quantity will be 0.0 in any case
                        stop_compute_bom = True

                    prod_min_quantities.append(prod_min_quantity)
                    if stop_compute_bom:
                        break
            produced_qty = uom_obj._compute_qty_obj(cr, uid,
                                                    bom.product_uom,
                                                    bom.product_qty,
                                                    bom.product_id.uom_id,
                                                    context=context)
            if prod_min_quantities:
                product_qty += min(prod_min_quantities) * produced_qty
            else:
                product_qty += produced_qty
        return product_qty

    def _product_available(self, cr, uid, ids, field_names=[],
                           arg=False, context=None):
        # We need available, virtual or immediately usable
        # quantity which is selected from company to compute Bom stock Value
        # so we add them in the calculation.
        context = context or self.pool['res.users'].context_get(cr, uid)
        start_time = datetime.now()
        user_obj = self.pool['res.users']
        comp_obj = self.pool['res.company']
        if 'bom_stock' in field_names:
            field_names.append('qty_available')
            field_names.append('immediately_usable_qty')
            field_names.append('virtual_available')

        res = {}
        for product_id in ids:
            res[product_id] = {}.fromkeys(field_names, 0.0)
        #todo think a mode to be parametric
        if False:
            product_stock_ids = self.search(cr, uid, [('id', 'in', ids), ('type', 'not in', ['consu', 'service'])], context=context)
        else:
            product_stock_ids = ids
        if product_stock_ids:  # if product_stock_ids is [] get_product_available on stock search for all product
            res.update(super(product_product, self)._product_available(cr, uid, product_stock_ids, field_names, arg, context))

        if 'bom_stock' in field_names:
            company = user_obj.browse(cr, uid, uid, context=context).company_id
            if not company:
                company_id = comp_obj.search(cr, uid, [], context=context)[0]
                company = comp_obj.browse(cr, uid, company_id, context=context)

            for product_id, stock_qty in res.iteritems():
                product = self.browse(cr, uid, product_id, context=context)
                res[product_id]['bom_stock'] = self._compute_bom_stock(cr, uid, product, stock_qty, company, context=context)
        end_time = datetime.now()
        duration_seconds = (end_time - start_time)
        duration = '{sec}'.format(sec=duration_seconds)
        _logger.info(u'_product_available get in {duration}'.format(duration=duration))
        return res

    def _get_boms(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for product_id in ids:
            result[product_id] = self.pool['mrp.bom'].search(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], context=context)
        return result

    def _get_prefered_supplier(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for product in self.browse(cr, uid, ids, context):
            result[product.id] = product.seller_ids and product.seller_ids[0].name.id or False
        return result
    
    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        start_time = datetime.now()
        context = context or self.pool['res.users'].context_get(cr, uid)
        if 'currency_id' in context:
            pricetype_obj = self.pool['product.price.type']
            price_type_id = pricetype_obj.search(cr, uid, [('field', '=', ptype)], context=context)[0]
            price_type_currency_id = pricetype_obj.browse(cr, uid, price_type_id, context).currency_id.id

        res = {}
        product_uom_obj = self.pool['product.uom']
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = product[ptype] or 0.0

            if ptype == 'standard_price' and product.is_kit:
                res[product.id] = product.cost_price or product.standard_price

            if ptype == 'list_price':
                res[product.id] = (res[product.id] * (product.price_margin or 1.0)) + product.price_extra
            if 'uom' in context:
                uom = product.uom_id or product.uos_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                                                                 uom.id, res[product.id], context['uom'])
            # Convert from price_type currency to asked one
            if 'currency_id' in context:
                # Take the price_type currency from the product field
                # This is right cause a field cannot be in more than one currency
                res[product.id] = self.pool['res.currency'].compute(cr, uid, price_type_currency_id,
                                                                        context['currency_id'], res[product.id], context=context)
        end_time = datetime.now()
        duration_seconds = (end_time - start_time)
        duration = '{sec}'.format(sec=duration_seconds)
        _logger.info(u'price_get get in {duration}'.format(duration=duration))
        return res
        
    _columns = {
        'date_inventory': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date Inventory"),
        'cost_price': fields.function(_cost_price,
                                      method=True,
                                      string=_('Cost Price (incl. BoM)'),
                                      digits_compute=dp.get_precision('Purchase Price'),
                                      help="The cost price is the standard price or, if the product has a bom, "
                                      "the sum of all standard price of its components. it take also care of the "
                                      "bom costing like cost per cylce."),
        'prefered_supplier': fields.function(_get_prefered_supplier, type='many2one', relation='res.partner', string='Prefered Supplier'),
        'is_kit': fields.function(_is_kit, fnct_search=_kit_filter, method=True, type="boolean", string="Kit"),
        'bom_lines': fields.function(_get_boms, relation='mrp.bom', string='Boms', type='one2many', method=True),
        'qty_available': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product UoM'),
            string='Quantity On Hand',
            help="Current quantity of products.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, "
                 "or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "typed as 'internal'."),
        'virtual_available': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product UoM'),
            string='Quantity Available',
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, "
                 "or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "typed as 'internal'."),
        'incoming_qty': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product UoM'),
            string='Incoming',
            help="Quantity of products that are planned to arrive.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods arriving to this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods arriving to the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "arriving to the Stock Location of the Warehouse of this "
                 "Shop, or any of its children.\n"
                 "Otherwise, this includes goods arriving to any Stock "
                 "Location typed as 'internal'."),
        'outgoing_qty': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product UoM'),
            string='Outgoing',
            help="Quantity of products that are planned to leave.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods leaving from this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods leaving from the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "leaving from the Stock Location of the Warehouse of this "
                 "Shop, or any of its children.\n"
                 "Otherwise, this includes goods leaving from any Stock "
                 "Location typed as 'internal'."),
        'immediately_usable_qty': fields.function(
            _product_available,
            digits_compute=dp.get_precision('Product UoM'),
            type='float',
            string='Immediately Usable',
            multi='qty_available',
            help="Quantity of products really available for sale." \
                 "Computed as: Quantity On Hand - Outgoing."),
        'bom_stock': fields.function(
            _product_available,
            digits_compute=dp.get_precision('Product UoM'),
            type='float',
            string='Bill of Materials Stock',
            help="Quantities of products based on Bill of Materials, "
                 "useful to know how much of this "
                 "product you could produce. "
                 "Computed as:\n "
                 "Reference stock of this product + "
                 "how much could I produce of this product with the BoM"
                 "Components",
            multi='qty_available'),
    }

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if self.pool['sale.order.line'].search(cr, uid, [('product_id', 'in', ids)], context=context):
            raise orm.except_orm(
                _("Error"),
                _("The product is used on same Sale Order, deactivate it"))
        if self.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', ids)], context=context):
            raise orm.except_orm(
                _("Error"),
                _("The product is used on same BOM, deactivate it"))
        return super(product_product, self).unlink(cr, uid, ids, context)

    def copy(self, cr, uid, product_id, default=None, context=None):
        """Copies the product and the BoM of the product"""
        context = context or self.pool['res.users'].context_get(cr, uid)
        copy_id = super(product_product, self).copy(cr, uid, product_id, default, context)

        if 'bom_ids' not in default:
            bom_obj = self.pool['mrp.bom']
            bom_ids = bom_obj.search(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], context=context)

            for bom_id in bom_ids:
                bom_obj.copy(cr, uid, bom_id, {'product_id': copy_id}, context=context)

        return copy_id

    def update_product_bom_price(self, cr, uid, ids, context=None):
        """
        This Function is call by scheduler.
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        for product in self.browse(cr, uid, ids, context):
            product.write({'standard_price': product.cost_price})
        return True

    def update_bom_price(self, cr, uid, context=None):
        """
        This Function is call by scheduler.
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        # search product with kit
        product_ids = self.search(cr, uid, [('is_kit', '=', True)], context=context)
        # digits_compute = dp.get_precision('Purchase Price')
        # digits_compute(cr)[1]
        delta = 10**-(self.pool['decimal.precision'].precision_get(cr, uid, 'Purchase Price'))
        for product in self.browse(cr, uid, product_ids, context):
            standard_price = round(product.standard_price + delta, self.pool['decimal.precision'].precision_get(cr, uid, 'Purchase Price'))
            cost_price = round(product.cost_price + delta, self.pool['decimal.precision'].precision_get(cr, uid, 'Purchase Price'))
            diff = round(abs(standard_price - cost_price), self.pool['decimal.precision'].precision_get(cr, uid, 'Purchase Price'))
            if diff > delta:
                self.write(cr, uid, product.id, {'standard_price': product.cost_price}, context)
        return True

    # from profilehooks import profile
    # @profile(immediate=True)
    def update_cache_price(self, cr, uid, context=None):
        """
        This Function is called by scheduler.
        """
        def _chunkIt(seq, size):
            newseq = []
            splitsize = 1.0 / size * len(seq)
            for line in range(size):
                newseq.append(seq[int(round(line * splitsize)): int(round((line + 1) * splitsize))])
            return newseq

        context = context or self.pool['res.users'].context_get(cr, uid)

        if ENABLE_CACHE:
            if context.get('product_ids', False):
                product_to_browse_ids = context['product_ids']
            else:
                cache_length = len(self.product_cost_cache)
                cache_ids = self.product_cost_cache.keys()
                cache_ids = [int(cache_id) for cache_id in cache_ids]
                product_ids = self.search(cr, uid, [], context=context)
                _logger.info(u'Cache {cache} of {product}'.format(cache=cache_length, product=len(product_ids)))
                product_to_browse_ids = list(set(product_ids) - set(cache_ids))
            if product_to_browse_ids:
                _logger.setLevel(logging.WARNING)

                if CACHE_TYPE == 'redis':
                    workers = multiprocessing.cpu_count()
                    if workers > 1:
                        workers = workers / 2
                    # threads = []
                    for split in _chunkIt(product_to_browse_ids, workers):
                        if split:
                            thread = self.UpdateCachePrice(cr, uid, self, split, context)
                            thread.start()
                            # threads.append(thread)

                    # for job in threads:
                    #     job.join()
                else:
                    for product in self.browse(cr, uid, product_ids, context):
                        # Get price to trigger cache calculation
                        cost_price = product.cost_price

        return True

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        res = super(product_product, self).write(cr, uid, ids, vals, context)
        changed_product = []
        if ENABLE_CACHE:
            if 'standard_price' in vals or 'seller_ids' in vals:
                bom_obj = self.pool['mrp.bom']
                changed_product = bom_obj.GetWhereUsed(cr, uid, ids, context)[1].keys()
            for product_id in changed_product:
                if int(product_id) in self.product_cost_cache:
                    del self.product_cost_cache[int(product_id)]
            # if CACHE_TYPE == 'redis':
            #     ctx = context.copy()
            #     ctx['product_ids'] = [int(product_id) for product_id in changed_product]
            #     self.update_cache_price(cr, uid, context=ctx)

        return res

    def fields_get(self, cr, uid, allfields=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        group_obj = self.pool['res.groups']
        ret = super(product_product, self).fields_get(cr, uid, allfields=allfields, context=context)

        if not (group_obj.user_in_group(cr, uid, uid, 'product_bom.group_modify_product', context=context) or group_obj.user_in_group(cr, uid, uid, 'product_bom.group_create_product', context=context)):
            for fields in ret.keys():
                ret[fields]['readonly'] = True
        return ret


# CANCEL CACHE IF SOMETHING CHANGE ON PRICELIST
class product_pricelist_item(orm.Model):

    _inherit = 'product.pricelist.item'

    def create(self, cr, uid, vals, context=None):
        res = super(product_pricelist_item, self).create(cr, uid, vals, context)
        if ENABLE_CACHE:
            self.pool['product.product'].product_cost_cache.empty()
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(product_pricelist_item, self).write(cr, uid, ids, vals, context)
        if ENABLE_CACHE:
            self.pool['product.product'].product_cost_cache.empty()
        return res

    def unlink(self, cr, uid, ids, context=None):
        res = super(product_pricelist_item, self).unlink(cr, uid, ids, context)
        if ENABLE_CACHE:
            self.pool['product.product'].product_cost_cache.empty()
        return res


# class pricelist_partnerinfo(orm.Model):
#
#     _inherit = 'pricelist.partnerinfo'
#
#     def create(self, cr, uid, vals, context=None):
#         res = super(pricelist_partnerinfo, self).create(cr, uid, vals, context)
#         if ENABLE_CACHE:
#             self.pool['product.product'].product_cost_cache.empty()
#         return res
#
#     def write(self, cr, uid, ids, vals, context=None):
#         res = super(pricelist_partnerinfo, self).write(cr, uid, ids, vals, context)
#         if ENABLE_CACHE:
#             self.pool['product.product'].product_cost_cache.empty()
#         return res
#
#     def unlink(self, cr, uid, ids, context=None):
#         res = super(pricelist_partnerinfo, self).unlink(cr, uid, ids, context)
#         if ENABLE_CACHE:
#             self.pool['product.product'].product_cost_cache.empty()
#         return res


