# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Denero Team. (<http://www.deneroteam.com>)
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


class purchase_requisition_partner(orm.TransientModel):
    _inherit = "purchase.requisition.partner"
    
    def _get_requisition_suppliers(self, cr, uid, context=None):
        res = []
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        requisition_id = context.get('active_id', None)
        prefered = context.get('prefered', False)

        product_id = False
        if prefered:
            product_id = context.get('product_id', False)

        if requisition_id:
            sql = """
                SELECT DISTINCT pso.name, pso.sequence
                FROM purchase_requisition AS req
                    INNER JOIN purchase_requisition_line AS reql ON reql.requisition_id = req.id
                    INNER JOIN product_supplierinfo AS pso ON pso.product_id = reql.product_id
                WHERE req.id = %d
            """ % (requisition_id)
            
            if prefered:
                sql += """AND pso.product_id={product_id}
                ORDER BY pso.sequence""".format(product_id=product_id)
            
            cr.execute(sql)
            data = cr.fetchall()
            
            if prefered and data:
                res = [data[0][0]]
            else:
                res = list(set([row[0] for row in data]))

        if not res:
            res = self.pool['res.partner'].search(cr, uid, [('supplier', '=', True)], context=context)
        return res
    
    _columns = {
        'supplier_ids': fields.many2many('res.partner', string='Suppliers', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True,) #domain="[('id', 'in', supplier_ids[0][2])]"),
    }
    _defaults = {
        'supplier_ids': _get_requisition_suppliers,
    }
