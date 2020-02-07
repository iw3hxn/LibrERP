# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Didotech SRL
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
from tools.translate import _
import math

OPTION_SELECTION = [
    ('0', 'Base'),
    ('1', 'Alternativa 1'),
    ('2', 'Alternativa 2'),
    ('3', 'Alternativa 3'),
]


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def get_color(self, cr, uid, ids, field_name, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        value = {}
        for line in self.browse(cr, uid, ids, context):
            if line.order_line_base_id:
                value[line.id] = line.order_line_base_id.color
            else:
                value[line.id] = 'black'
        return value

    _columns = {
        'option': fields.selection(OPTION_SELECTION, 'Opzione'),
        'order_line_base_id': fields.many2one('sale.order.line.base', 'Sezione', domain=[('order_id', '=', 'order_id')], select=True),
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True),
    }

    _defaults = {
        'option': '0'
    }

    _order = "option asc, sequence asc, id asc"

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

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(SaleOrderLine, self).default_get(cr, uid, fields, context)
        if context.get('order_line_base_ids', False):
            sale_order_line_base_obj = self.pool['sale.order.line.base']
            default = False
            for tupla_order_line_base_id in context.get('order_line_base_ids'):
                if tupla_order_line_base_id[0] == 4:  # linked
                    if sale_order_line_base_obj.browse(cr, uid, tupla_order_line_base_id[1]).default:
                        default = tupla_order_line_base_id[1]
                elif tupla_order_line_base_id[0] == 1:
                    if tupla_order_line_base_id[2].get('default', False):
                        default = tupla_order_line_base_id[1]
            if default:
                res.update(order_line_base_id=default)
        if context.get('sequence', False):
            res.update(sequence=int(context['sequence']))
        return res

    def create(self, cr, uid, values, context=None):
        order_line_base_model = self.pool['sale.order.line.base']

        context = context or self.pool['res.users'].context_get(cr, uid)
        values.update(is_store=True)

        if values.get('order_line_base_id', False) and values.get('order_id', False):
            for line_base_id in order_line_base_model.search(cr, uid, [('order_id', '=', values['order_id'])], context=context):
                origin_base_line_id = order_line_base_model.browse(cr, uid, line_base_id, context).origin_base_line_id.id
                if values['order_line_base_id'] == origin_base_line_id:
                    values['order_line_base_id'] = line_base_id

        new_line_id = super(SaleOrderLine, self).create(cr, uid, values, context)
        if 'new_line_ids' in context:
            context['new_line_ids'].append(new_line_id)
        else:
            context['new_line_ids'] = [new_line_id]
        return new_line_id

    def option_product_id_change(self, cr, uid, ids, product_id, qty, uom, qty_uos, uos, name, packaging, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        lang = context.get('lang')
        flag = False
        update_tax = True
        partner_id = context.get('partner_id')
        pricelist = context.get('pricelist_id')
        date_order = context.get('date_order')
        fiscal_position = context.get('fiscal_position')
        res = self.product_id_change(cr, uid, ids, pricelist, product_id, qty, uom, qty_uos, uos, name, partner_id,
                                     lang, update_tax, date_order, packaging, fiscal_position, flag, context=context)
        return res

    def button_duplicate(self, cr, uid, ids, context):
        for line in self.browse(cr, uid, ids, context):
            if line.order_id.state != 'draft':
                raise orm.except_orm(
                    u'Errore',
                    u'Si possono duplicare le righe solo di ordini in stato Draft')
            self.copy(cr, uid, line.id, default={
                'sequence': line.sequence + 2
            }, context=context)

        if line:
            order_id = line.order_id.id

        # view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'sale', 'view_order_form')
        # view_id = view and view[1] or False
        # DO NOT specify view_id, because of 'view_mode: page,form'
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'page,form',
            # 'view_id': [view_id],
            'target': 'current',
            'res_id': order_id,
        }

