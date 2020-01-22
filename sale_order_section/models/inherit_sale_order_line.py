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


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _index_name = 'sale_order_line_product_id_index'

    def _auto_init(self, cr, context={}):
        super(sale_order_line, self)._auto_init(cr, context)
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s', (self._index_name,))
        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON sale_order_line (product_id)'.format(name=self._index_name))

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit_uos * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uos_qty,
                                        line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)

            res[line.id] = taxes['total']  # float_round(taxes['total'], precision_rounding=0.001)
        return res

    def get_color(self, cr, uid, ids, field_name, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        value = {}
        for line in self.browse(cr, uid, ids, context):
            if line.order_line_base_id:
                value[line.id] = line.order_line_base_id.color
            else:
                value[line.id] = 'black'
        return value

    def _cost_price_sale_order_line_price(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = {
                'price_unit_discount': 0.0,
                'price_unit_discount_uos': 0.0,
                'price_subtotal': 0.0
            }
            disc = self.Calcolo_Sconto(cr, uid, ids, line.string_discount, line.price_unit, line.price_unit_uos, context).get('value')
            res[line.id].update({
                'price_unit_discount': disc['price_unit_discount'],
                'price_unit_discount_uos': disc['price_unit_discount_uos'],
                'price_subtotal': round(line.product_uos_qty, 3) * round(disc['price_unit_discount_uos'], 4)
            })

        return res

    def _get_product_available(self, product):
        vals = {
            'qty_available': 0,
            'qty_available_uos': 0,
            'virtual_available': 0,
            'virtual_available_uos': 0
        }
        if product.type != 'service':
            uos_coeff = product.get_uos_coeff()
            vals.update({
                'qty_available': product.qty_available or False,
                'qty_available_uos': product.qty_available * uos_coeff or False,
                'virtual_available': product.virtual_available or False,
                'virtual_available_uos': product.virtual_available * uos_coeff or False
            })
        return vals

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}

        if context.get('shop', False):
            context['warehouse'] = self.pool['sale.shop']._get_warehouse_id(cr, uid, context['shop'], context)
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = self._get_product_available(line.product_id)
        return res

    def _set_dummy(self, cr, uid, ids, name, value, arg, context=None):
        return True

    def _getlist_price_uos(self, cr, uid, ids, name, arg, context=None):
        res = {}

        for line in self.browse(cr, uid, ids, context=context):
            uos_coeff = line.product_id.get_uos_coeff()
            #
            # if line.product_id:
            #     uos_coeff = line.product_id.uos_coeff or 1
            # if uos_coeff == 0:
            #     uos_coeff = 1

            product_uos_qty = round(line.product_uom_qty * uos_coeff, 4)
            if abs(product_uos_qty - int(product_uos_qty)) < 0.005:
                product_uos_qty = int(product_uos_qty)

            res[line.id] = {
                'product_uos_qty': product_uos_qty,
                'product_uos': line.product_id and line.product_id.uos_id and line.product_id.uos_id.id or False,
                'price_unit_uos': round(line.price_unit / uos_coeff, 4)
            }
        return res

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
        res = super(sale_order_line, self).default_get(cr, uid, fields, context)
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

        new_line_id = super(sale_order_line, self).create(cr, uid, values, context)
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

