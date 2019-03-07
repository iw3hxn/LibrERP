# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2018 Carlo Vettore (carlo.vettore at didotech.com)
#
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
##############################################################################
from datetime import datetime

from dateutil.relativedelta import relativedelta
from openerp.osv import orm


class virtual_purchase_requisition_partner(orm.TransientModel):
    '''
    We need this class to disable view specific function view_init()
    '''
    
    _name = "virtual.purchase.requisition.partner"
    _inherit = "purchase.requisition.partner"

    def view_init(self, cr, uid, fields_list, context=None):
        return True

    def create_order(self, cr, uid, ids, context=None):
        """
             To Create a purchase orders .

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary
             @return: {}

        """
        if context is None:
            context = {}
        record_ids = context and context.get('active_ids', False)
        if record_ids:
            data = self.browse(cr, uid, ids, context)
            company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
            order_obj = self.pool['purchase.order']
            order_line_obj = self.pool['purchase.order.line']
            partner_obj = self.pool['res.partner']
            tender_line_obj = self.pool['purchase.requisition.line']
            pricelist_obj = self.pool['product.pricelist']
            prod_obj = self.pool['product.product']
            tender_obj = self.pool['purchase.requisition']
            acc_pos_obj = self.pool['account.fiscal.position']
            partner_id = data[0].partner_id.id

            supplier_data = partner_obj.browse(cr, uid, partner_id, context=context)

            delivery_address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
            list_line = []
            purchase_order_line = {}
            for requisition in tender_obj.browse(cr, uid, record_ids, context=context):
                location_id = requisition.warehouse_id.lot_input_id.id
                for line in requisition.line_ids:
                    supplier_info = [sinfo for sinfo in line.product_id.seller_ids if
                                     sinfo and sinfo.name.id == partner_id]
                    if not len(supplier_info):
                        continue
                    partner_list = sorted([(partner.sequence, partner) for partner in line.product_id.seller_ids if partner])
                    partner_rec = partner_list and partner_list[0] and partner_list[0][1] or False
                    uom_id = line.product_id.uom_po_id and line.product_id.uom_po_id.id or False

                    if requisition.date_start:
                        newdate = datetime.strptime(requisition.date_start, '%Y-%m-%d %H:%M:%S') - relativedelta(
                            days=company.po_lead)
                    else:
                        newdate = datetime.today() - relativedelta(days=company.po_lead)
                    delay = partner_rec and partner_rec.delay or 0.0
                    if delay:
                        newdate -= relativedelta(days=delay)

                    partner = partner_rec and partner_rec.name or supplier_data
                    pricelist_id = partner.property_product_pricelist_purchase and partner.property_product_pricelist_purchase.id or False
                    price = pricelist_obj.price_get(cr, uid, [pricelist_id], line.product_id.id, line.product_qty, False,
                                            {'uom': uom_id})[pricelist_id]
                    product = prod_obj.browse(cr, uid, line.product_id.id, context=context)

                    purchase_order_line = {
                        'name': product.partner_ref,
                        'product_qty': line.product_qty,
                        'product_id': line.product_id.id,
                        'product_uom': uom_id,
                        'price_unit': price,
                        'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                        'notes': product.description_purchase,
                    }
                    taxes_ids = line.product_id.product_tmpl_id.supplier_taxes_id
                    taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)
                    purchase_order_line.update({
                        'taxes_id': [(6, 0, taxes)]
                    })
                    list_line.append(purchase_order_line)

                if not len(list_line):
                    continue

                order_vals = {
                    'origin': requisition.purchase_ids and requisition.purchase_ids[0].origin or requisition.name,
                    'partner_id': partner_id,
                    'partner_address_id': delivery_address_id,
                    'pricelist_id': pricelist_id,
                    'location_id': location_id,
                    'company_id': requisition.company_id.id,
                    'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                    'requisition_id': requisition.id,
                    'notes': requisition.description,
                    'warehouse_id': requisition.warehouse_id.id and requisition.warehouse_id.id,
                    'location_id': location_id,
                    'company_id': requisition.company_id.id,
                }

                onchange_partner_vals = order_obj.onchange_partner_id(cr, uid, [], partner_id).get('value')
                for onchange_partner_key in onchange_partner_vals.keys():
                    if onchange_partner_key not in order_vals.keys():
                        order_vals[onchange_partner_key] = onchange_partner_vals[onchange_partner_key]

                shop_ids = self.pool['sale.shop'].search(cr, uid, [('warehouse_id', '=', requisition.warehouse_id.id and requisition.warehouse_id.id)], context=context)
                if shop_ids:
                    order_vals.update({'shop_id': shop_ids[0]})

                purchase_id = order_obj.create(cr, uid, order_vals, context)
                order_ids = []
                for order_line in list_line:
                    order_line.update({
                        'order_id': purchase_id
                    })
                    order_line_obj.create(cr, uid, order_line, context)
        return {'type': 'ir.actions.act_window_close'}

