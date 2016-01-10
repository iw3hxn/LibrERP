# -*- coding: utf-8 -*-

#################################################################################
# Autor: Mikel Martin (mikel@zhenit.com)
#    Copyright (C) 2012 ZhenIT Software (<http://ZhenIT.com>). All Rights Reserved
#    $Id$
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

from lxml import etree
from openerp.osv import fields, orm
from tools.translate import _


class order_merge(orm.TransientModel):
    """
    Merge order
    """

    _name = 'order.merge'
    _description = 'Use this wizard to merge draft orders from the same partner'

    _columns = {
        'merge_lines': fields.boolean('Merge order lines',
                                      help='Merge order lines with same product at the same price.'),
        'orders': fields.many2many('sale.order', 'sale_order_merge_rel', 'merge_id', 'order_id', 'Sale Order')
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(order_merge, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context,
                                                       toolbar=toolbar, submenu=False)
        parent = self.pool['sale.order'].browse(cr, uid, context['active_id'], context=context)

        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='orders']")
        for node in nodes:
            node.set('domain', '["&",("partner_id", "=", ' + str(parent.partner_id.id) + '), ("state", "=", "draft")]')
        res['arch'] = etree.tostring(doc)
        context['partner'] = parent.partner_id.id
        return res

    def default_get(self, cr, uid, fields, context=None):
        """
        """
        res = super(order_merge, self).default_get(cr, uid, fields, context=context)
        if context and 'active_ids' in context and context['active_ids']:
            res.update({'orders': context['active_ids']})
        return res

    def merge_orders(self, cr, uid, ids, context):

        data = self.browse(cr, uid, ids, context=context)[0]
        order_id = self.pool['sale.order'].merge_order(cr, uid, data.orders, data.merge_lines, context)

        mod_obj = self.pool['ir.model.data']
        res = mod_obj.get_object_reference(cr, uid, 'sale', 'view_order_form')
        res_id = res and res[1] or False,

        return {
            'name': 'Sale Order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res_id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': order_id and order_id[0] or False,
        }
