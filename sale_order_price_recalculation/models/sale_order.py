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
        'recalculate_prices': fields.boolean('Recalculate Prices')
    }

    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        ret = super(sale_order, self).onchange_pricelist_id(cr, uid, ids, pricelist_id, order_lines, context=context)
        if ret:
            ret.update({'value': {'recalculate_prices': True}})
        return ret

    def _get_price_recalculation_pricelist(self, line, res):
        line_value = {
            'discount': line.discount,
            'price_unit': res['value'].get('price_unit', False),
            'purchase_price': res['value'].get('purchase_price', False),
        }
        return line_value

    def _get_price_recalculation_pricelist_no_discount(self, line, res):
        line_value = {
            'discount': res['value'].get('discount', False),
            'price_unit': res['value'].get('price_unit', False),
            'purchase_price': res['value'].get('purchase_price', False),
        }
        return line_value

    def recalculate_prices(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for sale in self.browse(cr, uid, ids, context):
            for line in sale.order_line:
                order = line.order_id
                res = line.product_id_change(
                    order.pricelist_id.id, line.product_id.id,
                    qty=line.product_uom_qty, uom=line.product_uom.id,
                    qty_uos=line.product_uos_qty, uos=line.product_uos.id,
                    name=line.name, partner_id=order.partner_id.id, lang=False,
                    update_tax=True, date_order=order.date_order, packaging=False,
                    fiscal_position=order.fiscal_position.id, flag=False)
                line_value = self._get_price_recalculation_pricelist(line, res)
                line.write(line_value)
            sale.write({'recalculate_prices': False})
        return True

    def recalculate_prices_no_discount(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for sale in self.browse(cr, uid, ids, context):
            for line in sale.order_line:
                order = line.order_id
                res = line.product_id_change(
                    order.pricelist_id.id, line.product_id.id,
                    qty=line.product_uom_qty, uom=line.product_uom.id,
                    qty_uos=line.product_uos_qty, uos=line.product_uos.id,
                    name=line.name, partner_id=order.partner_id.id, lang=False,
                    update_tax=True, date_order=order.date_order, packaging=False,
                    fiscal_position=order.fiscal_position.id, flag=False)
                line_value = self._get_price_recalculation_pricelist_no_discount(line, res)
                line.write(line_value)
            sale.write({'recalculate_prices': False})
        return True
