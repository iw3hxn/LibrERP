# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2017 Didotech srl (<http://www.didotech.com>).
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


class purchase_order(orm.Model):
    """ Modificaciones de sale order para añadir la posibilidad de versionar el pedido de venta. """
    _inherit = "purchase.order"

    def action_previous_version(self, cr, uid, ids, default=None, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        if isinstance(ids, (int, long)):
            ids = [ids]

        default = default or {}
        context = context or self.pool['res.users'].context_get(cr, uid)

        attachment_obj = self.pool['ir.attachment']

        order_ids = []
        for purchase_order in self.browse(cr, uid, ids, context=context):
            vals = {
                'version': (purchase_order.version and purchase_order.version or 1) + 1,
                'date_order': fields.date.context_today(cr, uid, context),
            }

            if not purchase_order.purchase_version_id:
                vals['purchase_version_id'] = purchase_order.id

            context['versioning'] = True
            vals['name'] = (purchase_order.purchase_version_id and purchase_order.purchase_version_id.name or purchase_order.name) + u" V." + ustr(
                vals['version'])
            new_order_id = self.copy(cr, uid, purchase_order.id, vals, context)

            attachment_ids = attachment_obj.search(cr, uid, [('res_model', '=', 'purchase.order'), ('res_id', '=', purchase_order.id)], context=context)
            if attachment_ids:
                attachment_obj.write(cr, uid, attachment_ids, {'res_id': new_order_id, 'res_name': vals['name']}, context)

            purchase_order.write({'active': False})
            order_ids.append(new_order_id)

        mod_obj = self.pool['ir.model.data']
        res = mod_obj.get_object_reference(cr, uid, 'purchase', 'purchase_order_form')
        res_id = res and res[1] or False,

        return {
            'name': _('Purchase Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res_id,
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': order_ids and order_ids[0] or False,
        }

    def _get_version_ids(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = {}
        for purchase_order in self.browse(cr, uid, ids, context):
            if purchase_order.purchase_version_id:
                res[purchase_order.id] = self.search(cr, uid, ['|', ('purchase_version_id', '=', purchase_order.purchase_version_id.id),
                                                     ('id', '=', purchase_order.purchase_version_id.id),
                                                     ('version', '<', purchase_order.version), '|', ('active', '=', False),
                                                     ('active', '=', True)], context=context)
            else:
                res[purchase_order.id] = []
        return res

    _columns = {
        'purchase_version_id': fields.many2one('purchase.order', 'Orig version', required=False, readonly=False),
        'version': fields.integer('Version no.', readonly=True),
        'active': fields.boolean('Active', readonly=False, help="It indicates that the sales order is active."),
        'version_ids': fields.function(_get_version_ids, method=True, type="one2many", relation='purchase.order',
                                       string='Versions', readonly=True),
        'revision_note': fields.char('Reason', size=256, select=True),
        'last_revision_note': fields.related('purchase_version_id', 'revision_note', type='char', string="Last Revision Note", store=True),
    }

    _defaults = {
        'active': True,
        'version': 0,
    }

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
        return self.print_report(cr, uid, ids, 'purchase.report_purchase_quotation', context)
