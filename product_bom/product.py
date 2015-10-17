# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2014 Didotech srl (info@didotech.com)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
import decimal_precision as dp
from openerp.tools.translate import _
from openerp import tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import decimal_precision as dp

import time

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class product_product(orm.Model):
    """
    Inherit Product in order to add an "Bom Stock" field
    """
    _inherit = 'product.product'
    
    # def _get_prefered_supplier(self, cr, uid, ids, field_name, args, context):
    #     res = {}
    #     for line in self.browse(cr, uid, ids, context):
    #         res[line.id] = line.seller_ids and line.seller_ids[0].name.id or False
    #     return res

    def _compute_purchase_price(self, cr, uid, ids,
                                product_uom=None,
                                bom_properties=None,
                                context=None):
        '''
        Compute the purchase price, taking into account sub products and routing
        '''
        
        context = context or {}
        bom_properties = bom_properties or []
        
        bom_obj = self.pool['mrp.bom']
        uom_obj = self.pool['product.uom']

        res = {}
        ids = ids or []
        
        for product in self.browse(cr, uid, ids, context):
            # print(u'{product.id}: {product.name}'.format(product=product))
            bom_id = bom_obj._bom_find(cr, uid, product.id, product_uom=None, properties=bom_properties)
            if bom_id:
                sub_bom_ids = bom_obj.search(cr, uid, [('bom_id', '=', bom_id)])
                sub_products = bom_obj.browse(cr, uid, sub_bom_ids)
                
                price = 0.
                
                for sub_product in sub_products:
                    if sub_product.product_id.id == product.id:
                        error = "Product '{product.name}' (id: {product.id}) is referenced to itself".format(product=product)
                        _logger.error(error)
                        continue
                        
                    # std_price = sub_product.standard_price
                    std_price = sub_product.product_id.cost_price
                    qty = uom_obj._compute_qty(cr, uid,
                                               from_uom_id=sub_product.product_uom.id,
                                               qty=sub_product.product_qty,
                                               to_uom_id=sub_product.product_id.uom_po_id.id)
                    price += std_price * qty
                    
                if sub_products:
                    # Don't use browse when we already have it
                    bom = sub_products[0].bom_id
                else:
                    bom = bom_obj.browse(cr, uid, bom_id)
                
                if bom.routing_id:
                    for wline in bom.routing_id.workcenter_lines:
                        wc = wline.workcenter_id
                        cycle = wline.cycle_nbr
                        # hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) * (wc.time_efficiency or 1.0)
                        price += wc.costs_cycle * cycle + wc.costs_hour * wline.hour_nbr
                price /= bom.product_qty
                price = uom_obj._compute_price(cr, uid, bom.product_uom.id, price, bom.product_id.uom_id.id)
                res[product.id] = price
            else:
                # no BoM: use standard_price
                # use standard_price if no supplier indicated
                if product.prefered_supplier:
                    pricelist = product.prefered_supplier.property_product_pricelist_purchase and product.prefered_supplier.property_product_pricelist_purchase.id or False
                    ctx = {
                        'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    }
                    price = self.pool['product.pricelist'].price_get(cr, uid, [pricelist], product.id, 1, context=ctx)[pricelist] or 0
                    res[product.id] = price
                else:
                    res[product.id] = product.standard_price
                continue
        
        return res

    def get_cost_field(self, cr, uid, ids, context=None):
        return self._cost_price(cr, uid, ids, '', [], context)

    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        context = context or {}
        product_uom = context.get('product_uom')
        bom_properties = context.get('properties')
        res = self._compute_purchase_price(cr, uid, ids, product_uom, bom_properties)
        return res

    def _kit_filter(self, cr, uid, obj, name, args, context):
        if not args:
            return []
        bom_obj = self.pool['mrp.bom']
        for search in args:
            if search[0] == 'is_kit':
                if search[2]:
                    bom_ids = bom_obj.search(cr, uid, [('bom_id', '=', False)])
                    if bom_ids:
                        res = [bom.product_id.id for bom in bom_obj.browse(cr, uid, bom_ids, context)]
                        return [('id', 'in', res)]
                    else:
                        return [('id', 'in', [])]
        return []
    
    def _is_kit(self, cursor, user, ids, product_uom=None, bom_properties=None, context=None):
        if not len(ids):
            return []
        '''
        Show if have or not a bom
        '''
        context = context or {}
        bom_properties = bom_properties or []

        bom_obj = self.pool['mrp.bom']

        res = {}
        ids = ids or []

        for record in self.browse(cursor, user, ids, context):
            bom_id = bom_obj._bom_find(cursor, user, record.id, product_uom=None, properties=bom_properties)
            
            if not bom_id:
                res[record.id] = False
            else:
                res[record.id] = True
            
        return res
    
    """
    Inherit Product in order to add an "Bom Stock" field
    """
    def _bom_stock_mapping(self, cr, uid, context=None):
        return {'real': 'qty_available',
                'virtual': 'virtual_available',
                'immediately': 'immediately_usable_qty'}

    def _compute_bom_stock(self, cr, uid, product,
                           quantities, company, context=None):
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
                    if bom_qty >= line_product_qty:
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

    def _product_available(self, cr, uid, ids, field_names=None,
                           arg=False, context=None):
        # We need available, virtual or immediately usable
        # quantity which is selected from company to compute Bom stock Value
        # so we add them in the calculation.
        user_obj = self.pool['res.users']
        comp_obj = self.pool['res.company']
        if 'bom_stock' in field_names:
            field_names.append('qty_available')
            field_names.append('immediately_usable_qty')
            field_names.append('virtual_available')

        res = super(product_product, self)._product_available(
            cr, uid, ids, field_names, arg, context)

        if 'bom_stock' in field_names:
            company = user_obj.browse(cr, uid, uid, context=context).company_id
            if not company:
                company_id = comp_obj.search(cr, uid, [], context=context)[0]
                company = comp_obj.browse(cr, uid, company_id, context=context)

            for product_id, stock_qty in res.iteritems():
                product = self.browse(cr, uid, product_id, context=context)
                res[product_id]['bom_stock'] = \
                    self._compute_bom_stock(
                        cr, uid, product, stock_qty, company, context=context)
        return res
    
    def _get_boms(self, cr, uid, ids, field_name, arg, context):
        result = {}
        
        for product_id in ids:
            result[product_id] = self.pool['mrp.bom'].search(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)])
        
        return result
    
    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        context = context or {}
        if 'currency_id' in context:
            pricetype_obj = self.pool['product.price.type']
            price_type_id = pricetype_obj.search(cr, uid, [('field', '=', ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(cr, uid, price_type_id).currency_id.id

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
        return res
        
    _columns = {
        'cost_price': fields.function(_cost_price,
                                      method=True,
                                      string=_('Cost Price (incl. BoM)'),
                                      digits_compute=dp.get_precision('Sale Price'),
                                      help="The cost price is the standard price or, if the product has a bom, "
                                      "the sum of all standard price of its components. it take also care of the "
                                      "bom costing like cost per cylce."),
        'prefered_supplier': fields.related('seller_ids', 'name', type='many2one', relation='res.partner', string='Prefered Supplier'),
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

    def copy(self, cr, uid, product_id, default=None, context=None):
        """Copies the product and the BoM of the product"""
        context = context or {}
        copy_id = super(product_product, self).copy(cr, uid, product_id, default=default, context=context)

        bom_obj = self.pool['mrp.bom']
        bom_ids = bom_obj.search(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)], context=context)
        
        for bom_id in bom_ids:
            bom_obj.copy(cr, uid, bom_id, {'product_id': copy_id}, context=context)
        return copy_id


class product_pricelist_item(orm.Model):
    _inherit = "product.pricelist.item"

    def _price_field_get(self, cr, uid, context=None):
        result = super(product_pricelist_item, self)._price_field_get(cr, uid, context)
        result.append((-4, _('Cost Price include Bom')))
        return result

    _columns = {
        'base': fields.selection(_price_field_get, 'Based on', required=True, size=-1, help="The mode for computing the price for this rule."),
    }

class product_pricelist(orm.Model):
    _inherit = 'product.pricelist'

    def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        context = context or {}
        date = context.get('date') or time.strftime('%Y-%m-%d')
        date = date[0:10]

        products = map(lambda x: x[0], products_by_qty_by_partner)
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        price_type_obj = self.pool.get('product.price.type')

        if not products:
            return {}

        version = False
        for v in pricelist.version_id:
            if ((v.date_start is False) or (v.date_start <= date)) and ((v.date_end is False) or (v.date_end >= date)):
                version = v
                break
        if not version:
            raise orm.except_orm(_('Warning!'), _("At least one pricelist has no active version !\nPlease create or activate one."))
        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s)) '
                'AND (product_id IS NULL OR (product_id = any(%s))) '
                'AND ((categ_id IS NULL) OR (categ_id = any(%s))) '
                'AND (price_version_id = %s) '
            'ORDER BY sequence, min_quantity desc',
            (prod_tmpl_ids, prod_ids, categ_ids, version.id))

        item_ids = [x[0] for x in cr.fetchall()]
        items = self.pool.get('product.pricelist.item').browse(cr, uid, item_ids, context=context)

        price_types = {}

        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            results[product.id] = 0.0
            rule_id = False
            price = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = product_uom_obj._compute_qty(
                        cr, uid, context['uom'], qty, product.uom_id.id or product.uos_id.id)
                except orm.except_orm:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and \
                            (product.product_variant_count > 1 or product.product_variant_ids[0].id != rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == -1:
                    if rule.base_pricelist_id:
                        price_tmp = self._price_get_multi(cr, uid,
                                rule.base_pricelist_id, [(product,
                                qty, partner)], context=context)[product.id]
                        ptype_src = rule.base_pricelist_id.currency_id.id
                        price_uom_id = qty_uom_id
                        price = currency_obj.compute(cr, uid,
                                ptype_src, pricelist.currency_id.id,
                                price_tmp, round=False,
                                context=context)
                elif rule.base == -2:
                    seller = False
                    for seller_id in product.seller_ids:
                        if (not partner) or (seller_id.name.id != partner):
                            continue
                        seller = seller_id
                    if not seller and product.seller_ids:
                        seller = product.seller_ids[0]
                    if seller:
                        qty_in_seller_uom = qty
                        seller_uom = seller.product_uom.id
                        if qty_uom_id != seller_uom:
                            qty_in_seller_uom = product_uom_obj._compute_qty(cr, uid, qty_uom_id, qty, to_uom_id=seller_uom)
                        price_uom_id = seller_uom
                        for line in seller.pricelist_ids:
                            if line.min_quantity <= qty_in_seller_uom:
                                price = line.price

                elif rule.base == -4:
                    price = product.cost_price

                else:
                    if rule.base not in price_types:
                        price_types[rule.base] = price_type_obj.browse(cr, uid, int(rule.base))
                    price_type = price_types[rule.base]

                    # price_get returns the price in the context UoM, i.e. qty_uom_id
                    price_uom_id = qty_uom_id
                    price = currency_obj.compute(
                            cr, uid,
                            price_type.currency_id.id, pricelist.currency_id.id,
                            product_obj._price_get(cr, uid, [product], price_type.field, context=context)[product.id],
                            round=False, context=context)

                if price is not False:
                    price_limit = price
                    price = price * (1.0+(rule.price_discount or 0.0))
                    if rule.price_round:
                        price = tools.float_round(price, precision_rounding=rule.price_round)

                    convert_to_price_uom = (lambda price: product_uom_obj._compute_price(
                                                cr, uid, product.uom_id.id,
                                                price, price_uom_id))
                    if rule.price_surcharge:
                        price_surcharge = convert_to_price_uom(rule.price_surcharge)
                        price += price_surcharge

                    if rule.price_min_margin:
                        price_min_margin = convert_to_price_uom(rule.price_min_margin)
                        price = max(price, price_limit + price_min_margin)

                    if rule.price_max_margin:
                        price_max_margin = convert_to_price_uom(rule.price_max_margin)
                        price = min(price, price_limit + price_max_margin)

                    rule_id = rule.id
                break

            # Final price conversion to target UoM
            price = product_uom_obj._compute_price(cr, uid, price_uom_id, price, qty_uom_id)

            results[product.id] = (price, rule_id)
        return results