# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Didotech srl (<http://www.didotech.com>).
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


class purchase_order_line(orm.Model):
    _inherit = "purchase.order.line"
    _columns = {
        # 'active': fields.related('order_id', 'active', type='boolean', string='Active', store=False),
        'purchase_line_copy_id': fields.many2one('purchase.order.line', 'Orig version', required=False, readonly=False),
    }

    def copy_data(self, cr, uid, line_id, defaults=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        defaults = defaults or {}
        if context.get('versioning', False):
            defaults['purchase_line_copy_id'] = line_id
        return super(purchase_order_line, self).copy_data(cr, uid, line_id, defaults, context)

    def copy(self, cr, uid, line_id, default, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        if context.get('versioning', False):
            default['purchase_line_copy_id'] = line_id
        return super(purchase_order_line, self).copy(cr, uid, line_id, default, context)


