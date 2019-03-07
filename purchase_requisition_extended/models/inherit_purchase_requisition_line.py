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

from openerp.osv import orm, fields


class purchase_requisition_line(orm.Model):
    _inherit = 'purchase.requisition.line'

    def _get_prefered_supplier(self, cr, uid, ids, field_name, args, context):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'prefered_supplier': ' ',
                'multy_supplier': False
            }
            seller_ids = line.product_id.seller_ids
            if seller_ids:
                res[line.id].update({
                    'prefered_supplier': seller_ids[0].name.name,
                    'multy_supplier': True and len(seller_ids) > 1
                })

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
            if line.product_id:
                cr.execute(query.format(product_id=line.product_id.id, requisition_id=line.requisition_id.id, state=state))
                res[line.id] = cr.fetchall()[0][0]
            else:
                res[line.id] = False

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
    
    #  def _get_compound_qty(self, cr, uid, ids, field_name, args, context=None):
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
        'prefered_supplier': fields.function(_get_prefered_supplier, string='Prefered Supplier', type='char', readonly=True, method=True, multi='all'),
        'multy_supplier': fields.function(_get_prefered_supplier, string='Other Supplier', type='boolean', readonly=True, method=True, multi='all'),
        'draft': fields.function(_get_requisitions, arg='draft', string='Draft', type='float', readonly=True, method=True),
        'approved': fields.function(_get_requisitions, arg='approved', string='Confirmed', type='float', readonly=True, method=True),
        'color': fields.function(_get_color, string='Color', type='char', readonly=True, method=True),
        'seller_ids': fields.related('product_id', 'seller_ids', type='one2many', relation='product.supplierinfo', string='Partners')
        # 'compound_qty': fields.function(_get_compound_qty, string=_('Quantity'), method=True),
        # 'destination_ids': fields.one2many('purchase.requisition.line.destination', 'requisition_line_id', _('Products Distribution'))
    }

