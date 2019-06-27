# -*- coding: utf-8 -*-

#       Copyright 2012 Francesco OpenCode Apruzzese <f.apruzzese@andreacometa.it>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from openerp.osv import orm, fields
from openerp.tools.translate import _


class wzd_massive_price_change(orm.TransientModel):
    _name = "wzd.massive_price_change"

    _columns = {
        'name': fields.selection(
            (('mku', 'MarkUp'), ('fix', 'Fix Price')),
            'Standard Price MarkUp Type'),
        'mku_price_source': fields.selection(
            (('sale', 'Sale'), ('supplier_form', 'Supplier Form')),
            'Price Type Source'),
        'price_type': fields.selection(
            (('sale', 'Sale'), ('cost', 'Cost'), ('supplier_form', 'Supplier Form')),
            'Price Type'),
        'value': fields.float('Value', help="Insert a fix price or a value from 0 to 100 to markup old price"),
        'supplier_id': fields.many2one('res.partner', 'Supplier'),
        'no_update_if_less': fields.boolean('No Update if less')
    }

    def onchange_price_type(self, cr, uid, ids, price_type, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        supplier_ids = []
        product_supplierinfo_obj = self.pool['product.supplierinfo']
        product_supplierinfo_ids = product_supplierinfo_obj.search(cr, uid, [('product_id', 'in', context['active_ids'])], context=context)
        for product_supplierinfo in product_supplierinfo_obj.browse(cr, uid, product_supplierinfo_ids, context):
            if product_supplierinfo.name.id not in supplier_ids:
                supplier_ids.append(product_supplierinfo.name.id)
        res = {
            'value': {
                'mku_price_source': False,
                'no_update_if_less': False
            },
            'domain': {
                'supplier_id': [('id', 'in', supplier_ids)]
            }
        }

        return res

    def change(self, cr, uid, ids, context=None):
        wzd = self.browse(cr, uid, ids[0], context)

        # test if user have authorization
        product_obj = self.pool['product.product']

        if wzd.price_type == 'sale':
            if not self.pool['res.groups'].user_in_group(cr, uid, uid, 'product_bom.group_sell_price', context):
                raise orm.except_orm(_("You don't have Permission!"), _("You must be on group 'Show Sell Price'"))
        if wzd.price_type in ['cost', 'supplier_form']:
            if not self.pool['res.groups'].user_in_group(cr, uid, uid, 'product_bom.group_cost_price', context):
                raise orm.except_orm(_("You don't have Permission!"), _("You must be on group 'Show Cost Price'"))

        if wzd.price_type == 'sale':
            if wzd.name == 'fix':
                self.pool['product.product'].write(cr, uid, context['active_ids'], {'list_price': wzd.value}, context)
            else:
                for product in product_obj.browse(cr, uid,  context['active_ids'], context):
                    if wzd.mku_price_source == 'sale':
                        new_price = product.list_price + ((product.list_price * wzd.value) / 100.00)
                    elif wzd.mku_price_source == 'supplier_form':
                        if not product.seller_ids:
                            raise orm.except_orm(_("Need to define supplier for product {product}".format(product=product.name)))
                        old_price = product.seller_ids[0].pricelist_ids[0].price
                        new_price = (old_price * wzd.value) / 100.00

                    if wzd.no_update_if_less:
                        if new_price < product.list_price:
                            continue
                    product_obj.write(cr, uid, [product.id], {'list_price': new_price}, context)

        elif wzd.price_type == 'cost':
            if wzd.name == 'fix':
                self.pool['product.product'].write(cr, uid, context['active_ids'], {'standard_price': wzd.value}, context)
            else:
                for product in product_obj.browse(cr, uid,  context['active_ids'], context):
                    new_price = product.standard_price + ((product.standard_price * wzd.value) / 100.00)
                    product_obj.write(cr, uid, [product.id], {'standard_price': new_price}, context)
        else:
            for product in product_obj.browse(cr, uid,  context['active_ids'], context):
                for product_info in product.seller_ids:
                    if (wzd.supplier_id and product_info.name.id == wzd.supplier_id.id) or not wzd.supplier_id:
                        if product_info.pricelist_ids:
                            if wzd.name == 'fix':
                                product_info.pricelist_ids[0].write({'price': wzd.value})
                            else:
                                standard_price = product_info.pricelist_ids[0].price
                                new_price = standard_price + ((standard_price * wzd.value) / 100.00)
                                product_info.pricelist_ids[0].write({'price': new_price})

        return {'type': 'ir.actions.act_window_close'}

