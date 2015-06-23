# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2013-2014 Didotech srl (info at didotech.com)
#                          All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import orm, fields
import decimal_precision as dp


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    
    _columns = {
        'mrp_bom': fields.one2many('sale.order.line.mrp.bom', 'order_id', 'Bom Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'with_bom': fields.boolean(string='With BOM'),
    }
    
    _defaults = {
        'with_bom': False,
    }
    
    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False,
                          packaging=False, fiscal_position=False, flag=False, context=None):
        
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product_id, qty, uom, qty_uos, uos, name, partner_id,
                                                                lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        
        mrp_bom_obj = self.pool['mrp.bom']
        
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            if product.supply_method == 'produce':
                result['value']['with_bom'] = True
                
                mrp_bom_ids = mrp_bom_obj.search(cr, uid, [('product_id', '=', product_id), ])
                if mrp_bom_ids and len(mrp_bom_ids) == 1:
                    mrp_bom = mrp_bom_obj.browse(cr, uid, mrp_bom_ids[0])
                    #line_mrp_bom_obj = self.pool.get('sale.order.line.mrp.bom')
                    if mrp_bom.bom_lines:
                        result['value']['mrp_bom'] = []
                        for bom_line in mrp_bom.bom_lines:
                            line_bom = {
                                #'name': bom_line.name,
                                'product_id': bom_line.product_id.id,
                                'product_uom_qty': bom_line.product_qty,
                                'product_uom': bom_line.product_uom.id,
                                'price_unit': bom_line.product_id.standard_price
                            }
                            result['value']['mrp_bom'].append(line_bom)
            else:
                result['value']['with_bom'] = False
        ## {'value': result, 'domain': domain, 'warning': warning}
        return result

    def onchange_mrp_bom(self, cr, uid, ids, mrp_bom, product_id, context=None):
        uom_obj = self.pool['product.uom']
        bom_obj = self.pool['mrp.bom']
        
        mrp_bom_filtered = [bom_id for bom_id in mrp_bom if not (isinstance(bom_id, (tuple, list)) and bom_id and bom_id[0] == 2) and not bom_id[0] == 5]
        
        line_mrps = self.resolve_o2m_commands_to_record_dicts(cr, uid, 'mrp_bom', mrp_bom_filtered, context=context)
        
        # Attention! This lines dupplicate _compute_purchase_price() from product_bom.product module
        price = 0.
        
        for line_mrp in line_mrps:
            #print line_mrp
            if line_mrp['product_uom']:
                if isinstance(line_mrp['product_uom'], (tuple, list)):
                    uom_id = line_mrp['product_uom'][0]
                elif isinstance(line_mrp['product_uom'], int):
                    uom_id = line_mrp['product_uom']
                qty = uom_obj._compute_qty(cr, uid,
                                           from_uom_id=uom_id,
                                           qty=line_mrp['product_uom_qty'],
                                           to_uom_id=uom_id)
                price += line_mrp['price_unit'] * qty
            else:
                price += line_mrp['price_unit'] * line_mrp['product_uom_qty']
        
        bom_ids = bom_obj.search(cr, uid, [('product_id', '=', product_id), ('bom_id', '=', False)])
        if bom_ids:
            bom = bom_obj.browse(cr, uid, bom_ids[0])
            if bom.routing_id:
                for wline in bom.routing_id.workcenter_lines:
                    wc = wline.workcenter_id
                    cycle = wline.cycle_nbr
                    # hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) * (wc.time_efficiency or 1.0)
                    price += wc.costs_cycle * cycle + wc.costs_hour * wline.hour_nbr
            price /= bom.product_qty
            price = uom_obj._compute_price(cr, uid, bom.product_uom.id, price, bom.product_id.uom_id.id)
        
        mrp_bom_new = []
        for line in mrp_bom:
            if line[2] and not line[2].get('price_subtotal', False) and line[2].get('price_unit', False) and line[2].get('product_uom_qty', False):
                line[2]['price_subtotal'] = line[2]['price_unit'] * line[2]['product_uom_qty']
                mrp_bom_new.append(line)
        
        if mrp_bom_new:
            return {'value': {'purchase_price': price, 'mrp_bom': mrp_bom_new}}
        else:
            return {'value': {'purchase_price': price}}


class sale_order_line_mrp_bom(orm.Model):
    _name = 'sale.order.line.mrp.bom'
    _description = 'Sales Order Bom Line'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}

        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.price_unit * line.product_uom_qty
        return res
    
    _columns = {
        'name': fields.char('Note', size=256, select=True),
        'order_id': fields.many2one('sale.order.line', 'Order Reference', required=True, ondelete='cascade', select=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True), ('type', 'not in', ['service'])], change_default=True),
        'product_uom_qty': fields.float('Quantity (UoM)', digits_compute=dp.get_precision('Product UoS'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Sale Price')),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Sale Price')),
    }
    
    _order = 'sequence, id'
    _defaults = {
        'product_uom_qty': 1,
        'sequence': 10,
        'price_unit': 0.0,
    }

    def bom_product_id_change(self, cr, uid, ids, product_id, uom_id, product_qty, price_unit, context=None):
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id)
            #qty = self.pool['product.uom']._compute_qty(cr, uid,
            #                           from_uom_id=uom_id,
            #                           qty=product_qty,
            #                           to_uom_id=uom_id)
            return {'value': {
                'price_unit': price_unit or product.cost_price,
                'product_uom': product.uom_id.id,
            }}
        else:
            return {'value': {}}
