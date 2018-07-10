# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012-2014 Andrei Levin (andrei.levin at didotech.com)
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
from openerp import netsvc
from openerp.osv import orm, fields
from openerp.tools.translate import _


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
                purchase_id = order_obj.create(cr, uid, {
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
                }, context)
                order_ids = []
                for order_line in list_line:
                    order_line.update({
                        'order_id': purchase_id
                    })
                    order_line_obj.create(cr, uid, order_line, context)
        return {'type': 'ir.actions.act_window_close'}


class purchase_requisition(orm.Model):
    _inherit = "purchase.requisition"

    def tender_done(self, cr, uid, ids, context=None):
        res = super(purchase_requisition, self).tender_done(cr, uid, ids, context)
        wf_service = netsvc.LocalService("workflow")
        for tender in self.browse(cr, uid, ids, context):
            for purchase_order in tender.purchase_ids:
                if purchase_order.state in ['draft']:
                    wf_service.trg_validate(uid, 'purchase.order', purchase_order.id, 'purchase_cancel', cr)
        return res
    
    def request_prefered_suppliers(self, cr, uid, ids, context):
        if not len(ids) == 1:
            return True
        virtual_partner_obj = self.pool['virtual.purchase.requisition.partner']
        new_context = {'active_id': ids[0], 'prefered': True}
        products = {}
        suppliers = {}
        purchase_requisition_line_ids = self.pool['purchase.requisition.line'].search(cr, uid, [('requisition_id', '=', ids[0])], context=context)
        purchase_requisition_lines = self.pool['purchase.requisition.line'].browse(cr, uid, purchase_requisition_line_ids, context=context)
        
        # We need this 2 cycles construction to handle situation when there are
        # more requisition lines with the same product
        for line in purchase_requisition_lines:
            products[line.product_id.id] = ''
        for product_id in products.keys():
            new_context['product_id'] = product_id
            supplier = virtual_partner_obj._get_requisition_suppliers(cr, uid, context=new_context)
            if supplier:
                suppliers[supplier[0]] = ''
        if not suppliers:
            raise orm.except_orm(_('Missed Supplier !'), _('There are no Preferred Supplier'))
        for supplier_id in suppliers.keys():
            requisition_partner_id = virtual_partner_obj.create(cr, uid, {'partner_id': supplier_id}, context)
            virtual_partner_obj.create_order(cr, uid, [requisition_partner_id], context={'active_ids': ids})

        self.tender_in_progress(cr, uid, ids, context=None)
        return True
        
    def request_to_suppliers(self, cr, uid, ids, context):
        virtual_partner_obj = self.pool['virtual.purchase.requisition.partner']
        for requisition in self.browse(cr, uid, ids, context):
            suppliers = virtual_partner_obj._get_requisition_suppliers(cr, uid, context={'active_id': requisition.id})
            if not suppliers:
                raise orm.except_orm(_('Missed Supplier !'), _('There are no Supplier'))
            for supplier_id in suppliers:
                if supplier_id in filter(lambda x: x, [rfq.state != 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
                    continue
                requisition_partner_id = virtual_partner_obj.create(cr, uid, {'partner_id': supplier_id}, context)
                virtual_partner_obj.create_order(cr, uid, [requisition_partner_id], context={'active_ids': [requisition.id]})

        self.tender_in_progress(cr, uid, ids, context=None)
        return True


class purchase_requisition_line(orm.Model):
    _inherit = 'purchase.requisition.line'
    
    def _get_prefered_supplier(self, cr, uid, ids, field_name, args, context):
        res = {}
        virtual_partner_obj = self.pool['virtual.purchase.requisition.partner']
        
        requisition_lines = self.browse(cr, uid, ids, context=context)
        for line in requisition_lines:
            if line.product_id:
                supplier_ids = virtual_partner_obj._get_requisition_suppliers(cr, uid, context={
                    'active_id': line.requisition_id.id,
                    'prefered': True,
                    'product_id': line.product_id.id,
                })
                if supplier_ids:
                    supplier = self.pool['res.partner'].browse(cr, uid, supplier_ids[0], context)
                    res[line.id] = supplier.name
                else:
                    res[line.id] = ''
            else:
                res[line.id] = ''
        return res

    def _get_requisitions(self, cr, uid, ids, field_name, state, context):
        res = {}

        query = """SELECT SUM(product_qty)
            FROM purchase_requisition
            INNER JOIN purchase_order ON purchase_order.requisition_id = purchase_requisition.id
            INNER JOIN purchase_order_line ON purchase_order.id = purchase_order_line.order_id
            WHERE purchase_order_line.product_id={product_id}
            AND purchase_requisition.id={requisition_id}
            AND purchase_order.state NOT IN ('cancel')
            AND purchase_order.state IN ('{state}')
        """
        
        requisition_lines = self.browse(cr, uid, ids, context=context)
        for line in requisition_lines:
            cr.execute(query.format(product_id=line.product_id.id, requisition_id=line.requisition_id.id, state=state))
            res[line.id] = cr.fetchall()[0][0]
        
        return res
    
    def _get_color(self, cr, uid, ids, field_name, args, context):
        res = {}
        
        lines = self.browse(cr, uid, ids, context=context)
        if lines:
            query = """ SELECT row.product_id, SUM(product_qty)
                FROM purchase_requisition_line AS row
                WHERE row.requisition_id={requisition_id}
                GROUP BY product_id
            """
            cr.execute(query.format(requisition_id=lines[0].requisition_id.id))
            result = dict(cr.fetchall())
            
        for row in lines:
            if row.product_id.id in result:
                product_qty = result[row.product_id.id]
            else:
                product_qty = 0
                
            if product_qty <= row.approved:
                res[row.id] = 'green'
            elif product_qty <= row.draft:
                res[row.id] = 'orange'
            else:
                res[row.id] = 'red'
        return res
    
    #def _get_compound_qty(self, cr, uid, ids, field_name, args, context=None):
    #    result = {}
    #    lines = self.browse(cr, uid, ids)
    #    for line in lines:
    #        if line.product_qty:
    #            result[line.id] = line.product_qty
    #        else:
    #            sum = 0
    #            for sub_line in line.destination_ids:
    #                sum += sub_line.product_qty
    #            result[line.id] = sum
    #    return result
    
    _columns = {
        'prefered_supplier': fields.function(_get_prefered_supplier, string='Prefered Supplier', type='char', readonly=True, method=True),
        'draft': fields.function(_get_requisitions, arg='draft', string='Draft', type='float', readonly=True, method=True),
        'approved': fields.function(_get_requisitions, arg='approved', string='Confirmed', type='float', readonly=True, method=True),
        'color': fields.function(_get_color, string='Color', type='char', readonly=True, method=True),
        # 'compound_qty': fields.function(_get_compound_qty, string=_('Quantity'), method=True),
        # 'destination_ids': fields.one2many('purchase.requisition.line.destination', 'requisition_line_id', _('Products Distribution'))
    }

