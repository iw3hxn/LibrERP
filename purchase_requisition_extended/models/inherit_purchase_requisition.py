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

from openerp import netsvc
from openerp.osv import orm, fields
from openerp.tools.translate import _


class purchase_requisition(orm.Model):
    _inherit = "purchase.requisition"

    def __init__(self, registry, cr):
        """
            Add state "To Process"
        """
        res = super(purchase_requisition, self).__init__(registry, cr)
        options = [('to_progress', _('To Process'))]

        type_selection = self._columns['state'].selection
        for option in options:
            if option not in type_selection:
                type_selection.append(option)
        return res

    def tender_to_progress(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'to_progress'}, context=context)

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
        purchase_requisition_line_obj = self.pool['purchase.requisition.line']
        new_context = context.copy()
        new_context.update({'active_id': ids[0], 'prefered': True})
        products = {}
        suppliers = {}
        purchase_requisition_line_ids = purchase_requisition_line_obj.search(cr, uid, [('requisition_id', '=', ids[0])], context=context)
        purchase_requisition_lines = purchase_requisition_line_obj.browse(cr, uid, purchase_requisition_line_ids, context=context)
        
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
                ctx = context.copy()
                ctx.update({'active_ids': [requisition.id]})
                virtual_partner_obj.create_order(cr, uid, [requisition_partner_id], context=ctx)

        self.tender_in_progress(cr, uid, ids, context=context)
        return True

    _columns = {
        'product_id': fields.related('line_ids', 'product_id', type='many2one', relation='product.product',
                                     string='Product'),
    }
