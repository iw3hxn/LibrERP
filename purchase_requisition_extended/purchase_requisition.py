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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc


class virtual_purchase_requisition_partner(orm.TransientModel):
    '''
    We need this class to disable view specific function view_init()
    '''
    
    _name = "virtual.purchase.requisition.partner"
    _inherit = "purchase.requisition.partner"

    def view_init(self, cr, uid, fields_list, context=None):
        return True


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
        virtual_partner_obj = self.pool.get('virtual.purchase.requisition.partner')
        for requisition in self.browse(cr, uid, ids, context):
            suppliers = virtual_partner_obj._get_requisition_suppliers(cr, uid, context={'active_id': requisition.id})
            if not suppliers:
                raise orm.except_orm(_('Missed Supplier !'), _('There are no Supplier'))
            for supplier_id in suppliers:
                if supplier_id in filter(lambda x: x, [rfq.state != 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
                    continue
                requisition_partner_id = virtual_partner_obj.create(cr, uid, {'partner_id': supplier_id})
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
    
