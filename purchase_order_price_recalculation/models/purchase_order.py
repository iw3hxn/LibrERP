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


class purchase_order(orm.Model):
    _inherit = "purchase.order"

    _columns = {
        'recalculate_prices': fields.boolean('Recalculate Prices')
    }

    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines, context=None):
        res = {}
        if (not pricelist_id) or (not order_lines):
            return res
        else:
            res.update({'value': {'recalculate_prices': True}})
        return res

    def recalculate_prices(self, cr, uid, ids, context=None):
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        for purchase in self.browse(cr, uid, ids, context):
            for line in purchase.order_line:
                order = line.order_id
                res = line.onchange_product_id(
                    order.pricelist_id.id, line.product_id.id,
                    line.product_qty, line.product_uom.id,
                    order.partner_id.id, order.date_order, order.fiscal_position.id,
                    line.date_planned, line.name, notes=line.notes, context=context)
                line_vals = res['value'].copy()
                if 'taxes_id' in line_vals:
                    del line_vals['taxes_id']
                if 'product_purchase_order_history_ids' in line_vals:
                    del line_vals['product_purchase_order_history_ids']
                line.write(line_vals)
            purchase.write({'recalculate_prices': False})
        return True
