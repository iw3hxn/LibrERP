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

from tools.translate import _
from datetime import date, datetime

from openerp.osv import orm, fields
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import decimal_precision as dp


class order_requirement_line_suppliers(orm.Model):

    _name = 'order.requirement.line.suppliers'
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', readonly=True, states={'draft': [('readonly', False)]}),
        'supplier_ids': fields.many2many('res.partner', string='Suppliers', readonly=True, states={'draft': [('readonly', False)]}),
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain="[('id', 'in', supplier_ids[0][2])]", readonly=True, states={'draft': [('readonly', False)]}),
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoS'), readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Confirmed'),
            ('cancel', 'Cancelled')
        ], 'State', readonly=True),
        'order_requirement_line_id': fields.many2one('order.requirement.line', 'order_requirement_line_supplier_id', readonly=True),
        # 'temp_mrp_bom_ids': fields.related('order_requirement_line_id', 'temp_mrp_bom_ids', relation='temp.mrp.bom', type='many2many'),
        'temp_mrp_bom_ids': fields.one2many('temp.mrp.bom', 'order_requirement_line_suppliers_id', 'BOM'),
        'view_bom': fields.boolean('View BOM')
    }

    # It will work only with a REAL hierarchical structure, but mrp bom is NOT
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

    def get_temp_mrp_bom(self, cr, uid, bom_father, context):
        # Returns a list of VALS
        temp_mrp_bom_vals = []
        order_requirement_line_obj = self.pool[context['active_model']]
        order_requirement_line = order_requirement_line_obj.browse(cr, uid, context['active_id'], context)
        product_id = order_requirement_line.product_id

        if not product_id.bom_ids:
            return []

        def _get_rec(bom_rec):
            bom_children = bom_rec.child_complete_ids
            if not bom_children:
                return
            children_levels = self.get_children(bom_rec.child_complete_ids, 0)
            for bom in bom_children:
                if bom.product_id.type in ('product', 'consu'):
                    newbom_vals = {
                        'tmp_id': bom.id,
                        'tmp_parent_id': bom.bom_id.id,
                        # 'complete_name': '&nbsp;&nbsp;&nbsp;' * children_levels[bom.id]['level'] + bom.name,
                        'complete_name': '...' * children_levels[bom.id]['level'] + ' ' + bom.name,
                        # 'complete_name': 'Level =' + str(children_levels[bom.id]['level']) + '= ' + bom.name,
                        'name': bom.name,
                        'type': bom.type,
                        'bom_id': bom.bom_id.id,
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

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(order_requirement_line_suppliers, self).default_get(cr, uid, fields, context=context)
        order_requirement_line_obj = self.pool[context['active_model']]
        order_requirement_line = order_requirement_line_obj.browse(cr, uid, context['active_id'], context)

        if order_requirement_line.new_product_id:
            res['product_id'] = order_requirement_line.new_product_id.id
        elif order_requirement_line.product_id:
            res['product_id'] = order_requirement_line.product_id.id
        res['qty'] = order_requirement_line.qty
        res['state'] = 'draft'
        res['view_bom'] = True
        product = order_requirement_line.product_id

        # DEBUG
        # if product.bom_ids:
        #     bom = product.bom_ids[0]
        #     children = self.get_children(bom.bom_lines, 0)
        #     for c in children:
        #         print '   ' * c['level'] + ' ' + c['name']

        # temp_mrp_bom_vals = self.get_temp_mrp_bom(cr, uid, product.bom_ids[0], context)
        # res['temp_mrp_bom_ids'] = [(0, False, temp) for temp in temp_mrp_bom_vals]

        return res

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

            # temp_mrp_bom_obj = self.pool['temp.mrp.bom']
            order_requirement_line_obj = self.pool[context['active_model']]
            order_requirement_line = order_requirement_line_obj.browse(cr, uid, context['active_id'], context)

            # Update BOM according to new product
            if product.bom_ids:
                children_levels = self.get_children(product.bom_ids[0].bom_lines, 0)

                temp_mrp_bom_vals = self.get_temp_mrp_bom(cr, uid, product.bom_ids[0], context)
                result_dict['temp_mrp_bom_ids'] = [(0, False, temp) for temp in temp_mrp_bom_vals]

            if new_product_id == order_requirement_line.product_id.id:
                newvalue = False
            # else:
            #     newvalue = new_product_id
            # order_requirement_line_obj.write(cr, uid, order_requirement_line.id, {'new_product_id': newvalue}, context)

        else:
            result_dict.update({
                'supplier_id': False,
                'supplier_ids': [],
            })

        result_dict['view_bom'] = len(result_dict['temp_mrp_bom_ids']) > 0
        return {'value': result_dict}

    def onchange_children_product_id(self, cr, uid, ids, new_product_id, qty=0, supplier_id=False, context=None):
        pass

    def confirm_qty_supplier(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        purchase_order_obj = self.pool['purchase.order']
        purchase_order_line_obj = self.pool['purchase.order.line']
        order_requirement_line_obj = self.pool[context['active_model']]
        order_requirement_line = order_requirement_line_obj.browse(cr, uid, context['active_id'], context)

        orls = self.browse(cr, uid, ids[0], context)
        supplier_id = orls.supplier_id.id
        product_id = orls.product_id.id
        qty = orls.qty
        shop = order_requirement_line.order_id.sale_order_id.shop_id
        shop_id = shop.id

        purchase_order_ids = purchase_order_obj.search(cr, uid, [('partner_id', '=', supplier_id),
                                                                 ('shop_id', '=', shop_id),
                                                                 ('state', '=', 'draft')], limit=1, context=context)
        if not supplier_id:
            raise orm.except_orm(_(u'Error !'),
                                 _(u'There are no suppliers defined for product {0}'.format(orls.product_id.name)))

        if not purchase_order_ids:
            # Adding if no "similar" orders are presents
            purchase_order_values = purchase_order_obj.onchange_partner_id(cr, uid, [], supplier_id)['value']
            location_id = shop.warehouse_id.lot_stock_id.id

            order_line_values = purchase_order_line_obj.onchange_product_id(cr, uid, [], purchase_order_values['pricelist_id'],
                                                                            product_id, qty, uom_id=False, partner_id=supplier_id, date_order=False,
                                                                            fiscal_position_id=purchase_order_values['fiscal_position'],
                                                                            date_planned=False, price_unit=False, notes=False, context=context)['value']
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
            order_line_values['order_requirement_line_ids'] = [(4, order_requirement_line.id)]

            # Create order line and relationship with order_requirement_line
            purchase_order_line_obj.create(cr, uid, order_line_values, context)

        else:
            # Extending order if I have found orders to same supplier for the same shop

            # Take first order
            present_order_id = purchase_order_ids[0]
            present_order = purchase_order_obj.browse(cr, uid, present_order_id, context)

            # Search for same product in Product lines
            purchase_order_line_ids = purchase_order_line_obj.search(cr, uid, [('order_id', 'in', purchase_order_ids),
                                                                               ('product_id', '=', product_id)], context=context)
            if not purchase_order_line_ids:
                # Line must be created
                order_line_values = purchase_order_line_obj.onchange_product_id(cr, uid, [], present_order.pricelist_id.id,
                                                                                product_id, qty, uom_id=False, partner_id=supplier_id, date_order=False,
                                                                                fiscal_position_id=False, date_planned=False, price_unit=False, notes=False, context=context)['value']
                order_line_values['product_id'] = product_id
                order_line_values['order_id'] = present_order_id
                # Creating a new line and link to many2many field
                order_requirement_line_obj.write(cr, uid, order_requirement_line.id, {'purchase_order_line_ids': [(0, 0, order_line_values)]}, context)
            else:
                # Add qty to existing line
                order_line_id = purchase_order_line_ids[0]
                line = purchase_order_line_obj.browse(cr, uid, order_line_id, context)
                newqty = qty + line.product_qty
                purchase_order_line_obj.write(cr, uid, order_line_id, {'product_qty': newqty}, context)
                # Create a new relationship (? only if not already present?)
                order_requirement_line_obj.write(cr, uid, order_requirement_line.id, {'purchase_order_line_ids': [(4, order_line_id)]}, context)

                # Now order_line_id is the created or update purchase order line

        order_requirement_line_obj.write(cr, uid, order_requirement_line.id, {'state': 'done'}, context)

        # Counting lines in Draft state, for current order requirement
        lines_draft = len(order_requirement_line_obj.search(cr, uid, [('order_id', '=', order_requirement_line.order_id.id),
                                                                      ('state', '=ilike', 'draft')], context=context))
        if lines_draft == 0:
            # No more draft lefts
            order_requirement_obj = self.pool['order.requirement']
            order_requirement_obj.write(cr, uid, order_requirement_line.order_id.id, {'state': 'done'}, context)

        return {
            'type': 'ir.actions.act_window_close'
        }

        # def action_open_bom(self, cr, uid, ids, context = None):
        #     line_supplier = self.browse(cr, uid, ids, context)[0]
        #     view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'profile_legnolandia', 'view_order_requirement_bom_tree')
        #     view_id = view and view[1] or False
        #
        #     # bom_childs = line_supplier.product_id.bom_ids[0].child_complete_ids
        #     # self.create_temp_mrp_boms(cr, uid, bom_childs, context)
        #
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'name': _('Product BOM'),
        #         'res_model': 'temp.mrp.bom',
        #         'view_type': 'tree',
        #         'view_mode': 'tree',
        #         'view_id': [view_id],
        #         'domain': [('bom_id', '=', False), ('product_id', '=', line_supplier.product_id.id)],
        #         'target': 'new',
        #         'res_id': False
        #     }
