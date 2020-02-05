# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2020 Didotech SRL
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
import decimal_precision as dp
from openerp.osv import orm, fields

COLOR_SELECTION = [
    ('aqua', u"Aqua"),
    ('black', u"Nero"),
    ('blue', u"Blu"),
    ('cadetblue', u"Blu Cadetto"),
    ('darkblue', u"Blu Scuro"),
    ('brown', u"Marrone"),
    ('fuchsia', u"Fuchsia"),
    ('forestgreen', u"Verde Scuro"),
    ('green', u"Verde"),
    ('grey', u"Grigio"),
    ('red', u"Rosso"),
    ('orange', u"Arancione")
]


class SaleOrderLineBase(orm.Model):
    _name = 'sale.order.line.base'

    def _get_subtotal_line(self, cr, uid, ids, field_name, arg, context):
        sale_order_line_obj = self.pool['sale.order.line']
        res = {}
        for base_line_id in ids:
            res[base_line_id] = 0
            sale_order_line_ids = sale_order_line_obj.search(cr, uid, [('order_line_base_id', '=', base_line_id)], context=context)
            for sale_order_line in sale_order_line_obj.read(cr, uid, sale_order_line_ids, ['price_subtotal'], context=context):
                res[base_line_id] += sale_order_line['price_subtotal']
        return res

    _columns = {
        'sequence': fields.integer('Sequenza', required=True),
        'order_id': fields.many2one('sale.order', 'Ordine', required=True, ondelete='cascade', select=True),
        'name': fields.char('Descrizione', required=True),
        'color': fields.selection(COLOR_SELECTION, 'Colore'),
        'report_print': fields.boolean('Stampa Riepilogo'),
        'default': fields.boolean('Corrente'),
        'is_store': fields.boolean('Is Store'),
        'origin_base_line_id': fields.many2one('sale.order.line.base', 'Original base line', required=False),
        'subtotal': fields.function(_get_subtotal_line, type="float",
                                      method=True,  string="Sub Totale",
                                      digits_compute=dp.get_precision('Sale Price'),)
    }

    _defaults = {
        'report_print': True,
        'sequence': 1,
    }

    _order = "sequence asc"

    def action_check(self, cr, uid, line_ids, context):
        if not line_ids:
            return True
        line = self.browse(cr, uid, line_ids, context)[0]
        line.write({'default': not line.default})
        if not line.default:
            sale_order_line_base_ids = self.search(cr, uid, [('order_id', '=', line.order_id.id)], context=context)
            self.write(cr, uid, sale_order_line_base_ids, {'default': False}, context)
        line.write({'default': not line.default})
        return True

    def action_add(self, cr, uid, line_ids, context):
        if not line_ids:
            return True
        for line_id in line_ids:
            line = self.browse(cr, uid, line_id, context)
            self.write(cr, uid, line_id, {'sequence': line.sequence + 1}, context)
        return True

    def action_remove(self, cr, uid, line_ids, context):
        if not line_ids:
            return True
        for line in self.browse(cr, uid, line_ids, context):
            if line.sequence > 1.0:
                self.write(cr, uid, [int(line.id)], {'sequence': line.sequence - 1}, context)
        return True

    def create(self, cr, uid, values, context):
        values.update(is_store=True)
        origin_base_line_id = values.get('origin_base_line_id', False)
        new_base_line_id = super(SaleOrderLineBase, self).create(cr, uid, values, context)

        if context.get('new_line_ids') and origin_base_line_id:
            for order_line in self.pool['sale.order.line'].browse(cr, uid, context['new_line_ids']):
                if order_line.order_line_base_id and order_line.order_line_base_id.id == origin_base_line_id:
                    order_line.write({
                        'order_line_base_id': new_base_line_id
                    })

        return new_base_line_id

    def copy_data(self, cr, uid, line_base_id, default=None, context=None):
        line_base_copy = super(SaleOrderLineBase, self).copy_data(cr, uid, line_base_id, default=default, context=context)
        line_base_copy['origin_base_line_id'] = line_base_id
        return line_base_copy
