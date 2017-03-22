# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2017 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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

from openerp.addons.purchase.purchase import purchase_order


def monkey_copy(self, cr, uid, origin_id, default=None, context=None):
    if not default:
        default = {}

    context = context or self.pool['res.users'].context_get(cr, uid)

    if not default.get('shop_id', False):
        default['shop_id'] = self.default_get(cr, uid, ['shop_id'], context=None)['shop_id']
    default.update({
        'state': 'draft',
        'shipped': False,
        'invoice_ids': [],
        'picking_ids': [],
        'name': default.get('name', '/'),
    })
    return super(purchase_order, self).copy(cr, uid, origin_id, default, context=context)


purchase_order.copy = monkey_copy
