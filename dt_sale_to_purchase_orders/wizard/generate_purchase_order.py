# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-Today OpenERP SA (<http://www.openerp.com>).
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

from osv import fields, osv
from tools.translate import _

class generate_purchase_order(osv.osv_memory):
    _name = 'sale_to_purchase_order.generate_purchase_order'
    _description = 'Generate Purchase Order'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Supplier', required=True, domain="[('supplier','=',True)]"),
        'pricelist_id': fields.many2one('product.pricelist', 'Purchase Pricelist', required=True, domain="[('type','=','purchase')]",
                        help="This pricelist will be used, instead of the default one, for purchases from the current partner",),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True,),
    }
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id, context=context)
        if not partner:
            return {}
        if isinstance(partner, list):
            partner = partner[0]
        
        if partner.property_product_pricelist_purchase:
            return {'value': {'pricelist_id': partner.property_product_pricelist_purchase.id}}
        else:
            return {}
    
    def generate_purchase_order(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            sale_order_ids = [context['active_id']]
            sale_obj = self.pool.get('sale.order')
            sale_obj.generate_purchase_order(cr, uid, sale_order_ids, wizard.partner_id.id, wizard.pricelist_id.id, 
                                             wizard.warehouse_id.id, context=context)
        return { 'type': 'ir.actions.act_window_close'}
        
generate_purchase_order()

