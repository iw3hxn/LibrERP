# -*- encoding: utf-8 -*-
##############################################################################
#
# Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2010 - 2011 Avanzosc <http://www.avanzosc.com>
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import orm, fields


class sale_order(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'recalculate_discount': fields.boolean('Recalculate Discount'),
        'discount_rate': fields.float('Discount Rate', readonly=True, states={'draft': [('readonly', False)]})
    }

    def onchange_discount_rate(self, cr, uid, ids, discount_rate, context=None):
        recalculate_discount = True
        # if discount_rate == 0.0:
        #     recalculate_discount = False
        ret = {'value': {'recalculate_discount': recalculate_discount}}
        return ret

    def recalculate_discount(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for sale in self.browse(cr, uid, ids, context):
            # for line in sale.order_line:
            #     line.write({'discount': sale.discount_rate})
            # sale.write({'recalculate_prices': False})
            self.pool['sale.order.line'].write(cr, uid, [line.id for line in sale.order_line], {'discount': sale.discount_rate}, context)
        self.write(cr, uid, ids, {'recalculate_discount': False}, context)
        return True
