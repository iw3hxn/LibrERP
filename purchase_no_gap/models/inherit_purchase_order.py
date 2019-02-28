# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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


from openerp.osv import orm, fields


class purchase_order(orm.Model):
    _inherit = "purchase.order"

    _columns = {
        'purchase_order_request': fields.char('Purchase Order Request'),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=True,
                                   states={'draft': [('readonly', False)]}),
    }

    _defaults = {
        'name': '/',
    }

    def onchange_shop_id(self, cr, uid, ids, shop_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        value = {}
        if shop_id:
            shop = self.pool['sale.shop'].browse(cr, uid, shop_id, context)
            value['warehouse_id'] = shop.warehouse_id.id
        return {'value': value}

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if vals.get('date_order', False):
            context.update({'date': vals.get('date_order')})
        if vals.get('name', '/') == '/':
            sale_shop_obj = self.pool['sale.shop']
            shop_id = vals.get('shop_id', False)
            if not shop_id:
                warehouse_id = vals.get('warehouse_id', False)
                shop_ids = sale_shop_obj.search(cr, uid, [('warehouse_id', '=', warehouse_id)], limit=1, context=context)
                if shop_ids:
                    shop_id = shop_ids[0]
            shop = sale_shop_obj.browse(cr, uid, shop_id, context=context)
            if shop and shop.purchase_sequence_id:
                sequence = self.pool['ir.sequence'].next_by_id(cr, uid, shop.purchase_sequence_id.id)
            else:
                sequence = self.pool['ir.sequence'].get(cr, uid, 'purchase.order')
            vals.update({'name': sequence})
        return super(purchase_order, self).create(cr, uid, vals, context=context)

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for purchase in self.browse(cr, uid, ids, context):
            if purchase.shop_id and purchase.shop_id.purchase_confirmed_sequence_id:
                purchase_order_request = purchase.name
                sequence = self.pool['ir.sequence'].next_by_id(cr, uid, purchase.shop_id.purchase_confirmed_sequence_id.id)
                self.write(cr, uid, purchase.id, {'name': sequence, 'purchase_order_request': purchase_order_request}, context)
        res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context)
        return res
    
    def copy(self, cr, uid, ids, defaults, contex=None):
        defaults.update({
            'name': '/'
        })
        res = super(purchase_order, self).copy(cr, uid, ids, defaults, contex)
        return res
