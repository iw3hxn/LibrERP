# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Alejandro Núñez Liz$
#    $Omar Castiñeira Saavedra$
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
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
from tools import ustr
from tools.translate import _


class SaleOrder(orm.Model):
    """ Modificaciones de sale order para añadir la posibilidad de versionar el pedido de venta. """
    _inherit = "sale.order"

    def action_wait(self, cr, uid, ids, *args):
        res = super(SaleOrder, self).action_wait(cr, uid, ids, *args)
        context = self.pool['res.users'].context_get(cr, uid)
        for order in self.browse(cr, uid, ids, context):
            if order.shop_id and order.shop_id.sale_order_sequence_id:
                sequence = self.pool['ir.sequence'].next_by_id(cr, uid, order.shop_id.sale_order_sequence_id.id)
                new_order_vals = {
                    'name': sequence,
                    'original_quotation_name': order.name,
                    'original_quotation_date': order.date_order,
                }
                order.write(new_order_vals)
        return res

    def action_reactivate_version(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        order_state = context.get('order_state', '')
        if order_state not in ['draft', 'cancel', 'tech_validation', 'manager_validation', 'customer_validation', 'email_sent_validation', 'supervisor_validation']:
            raise orm.except_orm(_('Error!'),
                                 _("Not correct state in Order to Resume Version"))

        if isinstance(ids, (int, long)):
            ids = [ids]
        order_ids = []
        for sale in self.browse(cr, uid, ids, context):
            order_ids += self.search(cr, uid, ['|', ('sale_version_id', '=', sale.sale_version_id.id),
                                               ('id', '=', sale.sale_version_id.id), '|', ('active', '=', False),
                                               ('active', '=', True)], context=context)
            version = self.read(cr, uid, order_ids[0], ['version'])['version']
            sale.write({'active': True, 'version': version})

        order_ids_deactivate = list(set(order_ids) - set(ids))
        self.write(cr, uid, order_ids_deactivate, {'active': False}, context=context)

        mod_obj = self.pool['ir.model.data']
        res = mod_obj.get_object_reference(cr, uid, 'sale', 'view_order_form')
        res_id = res and res[1] or False,

        return {
            'name': _('Sale Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res_id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': ids and ids[0] or False,
        }

    def action_previous_version(self, cr, uid, ids, default=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if isinstance(ids, (int, long)):
            ids = [ids]

        default = default or {}
        context = context or self.pool['res.users'].context_get(cr, uid)

        attachment_obj = self.pool['ir.attachment']
        sale_order_line_obj = self.pool['sale.order.line']

        order_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            vals = {
                'version': (order.version and order.version or 1) + 1,
                'date_order': fields.date.context_today(cr, uid, context),
                'order_line': []
            }

            if not order.sale_version_id:
                vals['sale_version_id'] = order.id

            context['versioning'] = True
            vals['name'] = (order.sale_version_id and order.sale_version_id.name or order.name) + u" V." + ustr(
                vals['version'])

            new_order_id = self.copy(cr, uid, order.id, vals, context=context)

            old_order_lines_ids = self.read(cr, uid, order.id, ['order_line'], context)['order_line']
            for order_line_id in old_order_lines_ids:
                sale_order_line_obj.copy(cr, uid, order_line_id, {'order_id': new_order_id}, context=context)

            attachment_ids = attachment_obj.search(cr, uid,
                                                   [('res_model', '=', 'sale.order'), ('res_id', '=', order.id)],
                                                   context=context)
            if attachment_ids:
                attachment_obj.write(cr, uid, attachment_ids, {'res_id': new_order_id, 'res_name': vals['name']},
                                     context)

            order.write({'active': False})
            order_ids.append(new_order_id)

        mod_obj = self.pool['ir.model.data']
        res = mod_obj.get_object_reference(cr, uid, 'sale', 'view_order_form')
        res_id = res and res[1] or False,

        self.button_dummy(cr, uid, order_ids, context=context)

        return {
            'name': _('Sale Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res_id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': order_ids and order_ids[0] or False,
        }

    def _get_version_ids(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for sale in self.browse(cr, uid, ids, context):
            if sale.sale_version_id:
                res[sale.id] = self.search(cr, uid, ['|', ('sale_version_id', '=', sale.sale_version_id.id),
                                                     ('id', '=', sale.sale_version_id.id),
                                                     ('version', '<', sale.version), '|', ('active', '=', False),
                                                     ('active', '=', True)], context=context)
            else:
                res[sale.id] = []
        return res

    def _get_visible_original_quotation(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for sale in self.browse(cr, uid, ids, context):
            res[sale.id] = False
            if sale.original_quotation_name and sale.original_quotation_name != sale.name:
                res[sale.id] = True
        return res

    _columns = {
        'original_quotation_name': fields.char('Original Quotation Name'),
        'original_quotation_date': fields.date('Original Quotation Date'),
        'sale_version_id': fields.many2one('sale.order', 'Orig version', required=False, readonly=False),
        'version': fields.integer('Version no.', readonly=True),
        'active': fields.boolean('Active', readonly=False, help="It indicates that the sales order is active."),
        'version_ids': fields.function(_get_version_ids, method=True, type="one2many", relation='sale.order',
                                       string='Versions', readonly=True),
        'visible_original_quotation': fields.function(_get_visible_original_quotation, type="boolean",
                                                      string="visible original quotation")
    }

    _defaults = {
        'active': True,
        'version': 0,
        'name': '/',
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if vals.get('name', '/') == '/':
            shop = self.pool['sale.shop'].browse(cr, uid, vals['shop_id'], context=context)
            if shop and shop.sequence_id:
                sequence = self.pool['ir.sequence'].next_by_id(cr, uid, shop.sequence_id.id)
                vals.update({'name': sequence})
            else:
                sequence = self.pool['ir.sequence'].get(cr, uid, 'sale.order')
                vals.update({'name': sequence})

        if (not context or not context.get('versioning', False)) and vals.get('sale_version_id', False):
            del vals['sale_version_id']
            vals['version'] = 0

        return super(SaleOrder, self).create(cr, uid, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'original_quotation_name': False,
            'original_quotation_date': False,
        })
        return super(SaleOrder, self).copy(cr, uid, id, default, context)

    def print_report(self, cr, uid, ids, xml_id, context):
        def id_from_xml_id():
            report_obj = self.pool['ir.actions.report.xml']
            report_all = report_obj.search(cr, uid, [], context=context)
            report_xml_ids = report_obj.get_xml_id(cr, uid, report_all, context=context)

            for key in report_xml_ids.keys():
                xml_id_it = report_xml_ids[key]
                if xml_id_it == xml_id:
                    return key
            return False

        report_id = id_from_xml_id()
        report = self.pool['ir.actions.report.xml'].browse(cr, uid, report_id, context)
        data = {'model': report.model, 'ids': ids, 'id': ids[0]}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report.report_name,
            'datas': data,
            'context': context
        }

    def print_order(self, cr, uid, ids, context):
        return self.print_report(cr, uid, ids, 'sale.report_sale_order', context)
