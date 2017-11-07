# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime

import decimal_precision as dp
from openerp.osv import orm, fields

from tools.translate import _

class order_requirement_line(orm.Model):

    _name = 'order.requirement.line'

    _rec_name = 'product_id'

    def _stock_availability(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        warehouse_order_point_obj = self.pool['stock.warehouse.orderpoint']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            spare = 0
            warehouse = line.sale_order_id.shop_id.warehouse_id
            order_point_ids = warehouse_order_point_obj.search(cr, uid, [('product_id', '=', line.product_id.id), ('warehouse_id', '=', warehouse.id)], context=context, limit=1)
            if order_point_ids:
                spare = warehouse_order_point_obj.browse(cr, uid, order_point_ids, context)[0].product_min_qty

            res[line.id] = {
                'stock_availability': line.product_id and line.product_id.type != 'service' and line.product_id.qty_available or False,
                'spare': spare,
            }
        return res

    def get_color(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = 'black'
            if line.stock_availability < line.spare:
                res[line.id] = 'red'
        return res


    def get_children(self, object, level=0):
        result = {}

        def _get_rec(object, level):
            for l in object:
                res = {'name': l.name,
                       'pname': l.product_id.name,
                       'pcode': l.product_id.default_code,
                       'pqty': l.product_qty,
                       'uname': l.product_uom.name,
                       'code': l.code,
                       'level': level
                       }

                result[l.id] = res
                if l.child_complete_ids:
                    if level < 6:
                        level += 1
                    _get_rec(l.child_complete_ids, level)
                    if 0 < level < 6:
                        level -= 1
            return result

        children = _get_rec(object, level)

        return children

    def get_temp_mrp_bom(self, cr, uid, bom_ids, context):
        # Returns a list of VALS
        context = context or self.pool['res.users'].context_get(cr, uid)
        temp_mrp_bom_vals = []

        if not bom_ids:
            return []

        for bom_father in bom_ids:
            children_levels = self.get_children(bom_father.child_complete_ids, 0)

            def _get_rec(bom_rec):
                bom_children = bom_rec.child_complete_ids
                if not bom_children:
                    return
                for bom in bom_children:
                    if bom.product_id.type == 'product':
                        # coolname = u' {1} - {0} {2}'.format(bom.id, bom_rec.id, bom.name)
                        newbom_vals = {
                            'tmp_id': bom.id,
                            'tmp_parent_id': bom_rec.id,
                            'complete_name': '___' * children_levels[bom.id]['level'] + ' ' + bom.name,
                            # 'complete_name': '___' * children_levels[bom.id]['level'] + coolname,
                            # 'complete_name': 'Level =' + str(children_levels[bom.id]['level']) + '= ' + bom.name,
                            'name': bom.name,
                            'type': bom.type,
                            # 'bom_id': bom.bom_id.id,
                            'product_id': bom.product_id.id,
                            'product_qty': bom.product_qty,
                            'product_uom': bom.product_uom.id,
                            'product_efficiency': bom.product_efficiency,
                            'routing_id': bom.routing_id.id,
                            'company_id': bom.company_id.id
                        }
                        temp_mrp_bom_vals.append(newbom_vals)
                        _get_rec(bom)

            _get_rec(bom_father)
        return temp_mrp_bom_vals

    def _get_or_create_temp_mrp(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        view_bom = 'view_bom' in context and context['view_bom']
        if not view_bom:
            return {}
        res = {}
        for line in self.browse(cr, uid, ids, context):
            if line._temp_mrp_bom_ids:
                # for t in line._temp_mrp_bom_ids:
                #     res[t.id] = self.read(cr, uid, t.id, None, context)
                res[line.id] = [t.id for t in line._temp_mrp_bom_ids]
            else:
                if line.new_product_id:
                    product = line.new_product_id
                elif line.product_id:
                    product = line.product_id
                temp_mrp_bom_vals = self.get_temp_mrp_bom(cr, uid, product.bom_ids, context)
                res[line.id] = [(0, False, temp) for temp in temp_mrp_bom_vals]
        return res

    _columns = {
        'new_product_id': fields.many2one('product.product', 'Choosen Product', readonly=True,
                                          states={'draft': [('readonly', False)]}),
        'product_id': fields.many2one('product.product', 'Original Product', readonly=True),
        'is_manufactured': fields.boolean('Manufacture'),
        'supplier_ids': fields.many2many('res.partner', string='Suppliers', readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain="[('id', 'in', supplier_ids[0][2])]",
                                       readonly=True, states={'draft': [('readonly', False)]}),
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoS'), states={'draft': [('readonly', False)]}),
        'stock_availability': fields.function(_stock_availability, method=True, multi='stock_availability', type='float', string='Stock Availability', readonly=True),
        'spare': fields.function(_stock_availability, method=True, multi='stock_availability', type='float', string='Spare', readonly=True),
        'order_requirement_id': fields.many2one('order.requirement', 'Order Reference', required=True, ondelete='cascade', select=True),
        'sale_order_id': fields.related('order_requirement_id', 'sale_order_id', string='Sale Order', relation='sale.order', type='many2one', readonly=True),
        'sequence': fields.integer('Sequence',
                                   help="Gives the sequence order when displaying a list of sales order lines."),
        'state': fields.selection(
            [('cancel', 'Cancelled'), ('draft', 'Draft'), ('done', 'Done')], 'State', required=True, readonly=True,
        ),
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True),
        'purchase_order_line_ids': fields.many2many('purchase.order.line', string='Purchase Order lines'),
        '_temp_mrp_bom_ids': fields.one2many('temp.mrp.bom', 'order_requirement_line_id', 'BoM Hierarchy'),
        'temp_mrp_bom_ids': fields.function(_get_or_create_temp_mrp, relation='temp.mrp.bom', string="BoM Hierarchy", method=True, type='one2many'),
    }

    _defaults = {
        'state': 'draft',
        'sequence': 10,
    }

    def fields_get(self, cr, uid, allfields=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        ret = super(order_requirement_line, self).fields_get(cr, uid, allfields=allfields, context=context)
        view_bom = 'view_bom' in context and context['view_bom']
        ret['temp_mrp_bom_ids']['invisible'] = not view_bom
        # ret['confirm_qty_supplier']['invisible'] = not view_bom

        return ret

    def onchange_product_id(self, cr, uid, ids, new_product_id, qty=0, supplier_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        supplierinfo_obj = self.pool['product.supplierinfo']
        # result_dict = {}
        result_dict = {'temp_mrp_bom_ids': []}
        if new_product_id:
            product = self.pool['product.product'].browse(cr, uid, new_product_id, context)
            if not supplier_id:
                # --find the supplier
                supplier_info_ids = supplierinfo_obj.search(cr, uid,
                                                            [('product_id', '=', product.product_tmpl_id.id)],
                                                            order="sequence", context=context)
                supplier_infos = supplierinfo_obj.browse(cr, uid, supplier_info_ids, context=context)
                seller_ids = [info.name.id for info in supplier_infos]

                if seller_ids:
                    result_dict.update({
                        'supplier_id': seller_ids[0],
                        'supplier_ids': seller_ids,
                    })
                else:
                    result_dict.update({
                        'supplier_id': False,
                        'supplier_ids': [],
                    })

            # Update BOM according to new product
            if product.bom_ids:
                temp_mrp_bom_vals = self.get_temp_mrp_bom(cr, uid, product.bom_ids, context)
                result_dict['temp_mrp_bom_ids'] = [(0, False, temp) for temp in temp_mrp_bom_vals]

        else:
            result_dict.update({
                'supplier_id': False,
                'supplier_ids': [],
            })

        result_dict['view_bom'] = len(result_dict['temp_mrp_bom_ids']) > 0
        return {'value': result_dict}


    def _purchase(self, cr, uid, line, context):
        purchase_order_obj = self.pool['purchase.order']
        purchase_order_line_obj = self.pool['purchase.order.line']

        supplier_id = line.supplier_id.id
        if not supplier_id:
            raise orm.except_orm(_(u'Error !'),
                                 _(u'There are no suppliers defined for product {0}'.format(line.product_id.name)))
        product_id = line.product_id.id
        qty = line.qty
        shop = line.sale_order_id.shop_id
        shop_id = shop.id

        purchase_order_ids = purchase_order_obj.search(cr, uid, [('partner_id', '=', supplier_id),
                                                                 ('shop_id', '=', shop_id),
                                                                 ('state', '=', 'draft')], limit=1, context=context)

        if not purchase_order_ids:
            # Adding if no "similar" orders are presents
            purchase_order_values = purchase_order_obj.onchange_partner_id(cr, uid, [], supplier_id)['value']
            location_id = shop.warehouse_id.lot_stock_id.id

            order_line_values = \
            purchase_order_line_obj.onchange_product_id(cr, uid, [], purchase_order_values['pricelist_id'],
                                                        product_id, qty, uom_id=False, partner_id=supplier_id,
                                                        date_order=False,
                                                        fiscal_position_id=purchase_order_values['fiscal_position'],
                                                        date_planned=False, price_unit=False, notes=False,
                                                        context=context)['value']
            # First create order

            purchase_id = purchase_order_obj.create(cr, uid, {
                'shop_id': shop_id,
                'partner_id': supplier_id,
                'partner_address_id': purchase_order_values['partner_address_id'],
                'pricelist_id': purchase_order_values['pricelist_id'],
                'fiscal_position': purchase_order_values['fiscal_position'],
                'invoice_method': 'manual',
                'location_id': location_id,
                'payment_term': purchase_order_values['payment_term'],
            }, context=context)

            order_line_values['product_id'] = product_id
            order_line_values['order_id'] = purchase_id
            order_line_values['order_requirement_line_ids'] = [(4, line.id)]

            # Create order line and relationship with order_requirement_line
            purchase_order_line_obj.create(cr, uid, order_line_values, context)

        else:
            # Extending order if I have found orders to same supplier for the same shop

            # Take first order
            present_order_id = purchase_order_ids[0]
            present_order = purchase_order_obj.browse(cr, uid, present_order_id, context)

            # Search for same product in Product lines
            purchase_order_line_ids = purchase_order_line_obj.search(cr, uid, [('order_id', 'in', purchase_order_ids),
                                                                               ('product_id', '=', product_id)],
                                                                     context=context)
            if not purchase_order_line_ids:
                # Line must be created
                order_line_values = purchase_order_line_obj.onchange_product_id(cr, uid, [], present_order.pricelist_id.id,
                                                            product_id, qty, uom_id=False, partner_id=supplier_id,
                                                            date_order=False,
                                                            fiscal_position_id=False, date_planned=False,
                                                            price_unit=False, notes=False, context=context)['value']
                order_line_values['product_id'] = product_id
                order_line_values['order_id'] = present_order_id
                # Creating a new line and link to many2many field
                self.write(cr, uid, line.id, {'purchase_order_line_ids': [(0, 0, order_line_values)]}, context)
            else:
                # Add qty to existing line
                order_line_id = purchase_order_line_ids[0]
                line = purchase_order_line_obj.browse(cr, uid, order_line_id, context)
                newqty = qty + line.product_qty
                purchase_order_line_obj.write(cr, uid, order_line_id, {'product_qty': newqty}, context)
                # Create a new relationship (? only if not already present?)
                self.write(cr, uid, line.id, {'purchase_order_line_ids': [(4, order_line_id)]}, context)
                # Now order_line_id is the created or update purchase order line

    def _manufacture(cr, uid, line, context):
        pass


    def confirm_suppliers(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)

        for line in self.browse(cr, uid, ids, context):
            if line.is_manufactured:
                self._manufacture(cr, uid, line, context)
            else:
                self._purchase(cr, uid, line, context)

            self.write(cr, uid, line.id, {'state': 'done'}, context)

            # Counting lines in Draft state, for current order requirement
            lines_draft = len(self.search(cr, uid, [('order_id', '=', line.order_id.id),
                                                                          ('state', '=ilike', 'draft')], context=context))
            if lines_draft == 0:
                # No more draft lefts
                order_requirement_obj = self.pool['order.requirement']
                order_requirement_obj.write(cr, uid, line.order_id.id, {'state': 'done'}, context)

        return {
            'type': 'ir.actions.act_window_close'
        }

    def action_open_bom(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        line = self.browse(cr, uid, ids, context)[0]

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'sale_order_requirement', 'view_order_requirement_line_form')
        view_id = view and view[1] or False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Product BOM'),
            'res_model': 'order.requirement.line',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            'context': {'view_bom': True},
            'res_id': line.id
        }
