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
        'price_type': fields.selection(
            (('sale', 'Sale'), ('cost', 'Cost')),
            'Price Type'),
        'value': fields.float('Value', help="Insert a fix price or a value from 0 to 100 to markup old price"),
    }

    def change(self, cr, uid, ids, context={}):
        wzd = self.browse(cr, uid, ids[0], context)

        # test if user have autorization

        if wzd.price_type == 'sale':
            if not self.pool['res.groups'].user_in_group(cr, uid, uid, 'product_bom.group_sell_price', context):
                raise orm.except_orm(_("You don't have Permission!"), _("You must be on group 'Show Sell Price'"))
        if wzd.price_type == 'cost':
            if not self.pool['res.groups'].user_in_group(cr, uid, uid, 'product_bom.group_cost_price', context):
                raise orm.except_orm(_("You don't have Permission!"), _("You must be on group 'Show Cost Price'"))

        if wzd.price_type == 'sale':
            if wzd.name == 'fix':
                self.pool['product.product'].write(cr, uid, context['active_ids'], {'list_price': wzd.value}, context)
            else:
                product_obj = self.pool['product.product']
                for ids in context['active_ids']:
                    product = product_obj.browse(cr, uid, ids, context)
                    new_price = product.list_price + ((product.list_price * wzd.value) / 100.00)
                    product_obj.write(cr, uid, [ids, ], {'list_price': new_price}, context)
        else:
            if wzd.name == 'fix':
                self.pool['product.product'].write(cr, uid, context['active_ids'], {'standard_price': wzd.value}, context)
            else:
                product_obj = self.pool['product.product']
                for ids in context['active_ids']:
                    product = product_obj.browse(cr, uid, ids, context)
                    new_price = product.standard_price + ((product.standard_price * wzd.value) / 100.00)
                    product_obj.write(cr, uid, [ids, ], {'standard_price': new_price}, context)

        return {'type': 'ir.actions.act_window_close'}

