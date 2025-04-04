# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012-2015 Didotech (<http://www.didotech.com>).
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

from openerp.addons.sale_subscriptions.models.sale_order import ORDER_DURATION
from openerp.osv import orm, fields


class ProductProduct(orm.Model):
    _inherit = "product.product"

    _columns = {
        'subscription': fields.boolean('Subscription'),
        'order_duration': fields.selection(ORDER_DURATION, 'Subscription Duration'),
        'subscription_product_id': fields.many2one('product.product', 'Product Connected', domain=[('type', '!=', 'service')]),
    }

    _defaults = {
        'order_duration': 365,
    }

    def onchange_subscription(self, cr, uid, ids, subscription, type, context=None):
        if not subscription:
            return {
                'value': {'subscription_product_id': False}
            }
        return {}
