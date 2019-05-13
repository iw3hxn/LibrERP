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


class purchase_requisition_partner(orm.TransientModel):
    '''
    We need this class to disable view specific function view_init()
    '''
    
    # _name = "purchase.requisition.partner"
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

            partner = partner_obj.browse(cr, uid, partner_id, context=context)

            delivery_address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
            list_line = []
            purchase_order_line_vals = {}
            for requisition in tender_obj.browse(cr, uid, record_ids, context=context):
                location_id = requisition.warehouse_id.lot_input_id.id
                # partner_list = sorted(
                #     [(partner.sequence, partner) for partner in line.product_id.seller_ids if partner])
                # partner_rec = partner_list and partner_list[0] and partner_list[0][1] or False
                # partner = partner_rec and partner_rec.name or supplier_data
                pricelist_id = partner.property_product_pricelist_purchase and partner.property_product_pricelist_purchase.id or False

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
                }
                onchange_partner_vals = order_obj.onchange_partner_id(cr, uid, [], partner_id).get('value')
                for onchange_partner_key in onchange_partner_vals.keys():
                    if onchange_partner_key not in order_vals.keys():
                        order_vals[onchange_partner_key] = onchange_partner_vals[onchange_partner_key]

                shop_ids = self.pool['sale.shop'].search(cr, uid, [
                    ('warehouse_id', '=', requisition.warehouse_id.id and requisition.warehouse_id.id)],
                                                         context=context)
                if shop_ids:
                    order_vals.update({'shop_id': shop_ids[0]})

                for line in requisition.line_ids:
                    supplier_info = [sinfo for sinfo in line.product_id.seller_ids if
                                     sinfo and sinfo.name.id == partner_id]
                    if not len(supplier_info):
                        continue

                    uom_id = line.product_id.uom_po_id and line.product_id.uom_po_id.id or False

                    if requisition.date_start:
                        newdate = datetime.strptime(requisition.date_start, '%Y-%m-%d %H:%M:%S') - relativedelta(days=company.po_lead)
                    else:
                        newdate = datetime.today() - relativedelta(days=company.po_lead)
                    delay = supplier_info and supplier_info[0].delay or 0.0
                    if delay:
                        newdate -= relativedelta(days=delay)

                    seller_price, qty, default_uom_po_id, date_planned = tender_obj._seller_details(cr, uid, line, partner, context=context)
                    purchase_order_line_vals = order_line_obj.onchange_product_id(cr, uid, [], order_vals['pricelist_id'], line.product_id.id, line.product_qty, uom_id, partner_id, False,
                                                                                           order_vals['fiscal_position'],
                                                                                           date_planned=date_planned,
                                                                                           name=line.product_id.partner_ref,
                                                                                           price_unit=False,
                                                                                           notes=line.product_id.description_purchase,
                                                                                           context=context).get('value')
                    purchase_order_line_vals.update({
                        'taxes_id': [(6, 0, purchase_order_line_vals.get('taxes_id'))],
                        'product_id': line.product_id.id
                    })
                    if 'product_purchase_order_history_ids' in purchase_order_line_vals:
                        del purchase_order_line_vals['product_purchase_order_history_ids']
                    list_line.append(purchase_order_line_vals)

                if not len(list_line):
                    continue

                order_vals['order_line'] = [(0, 0, line) for line in list_line]

                purchase_id = order_obj.create(cr, uid, order_vals, context)

        return {'type': 'ir.actions.act_window_close'}