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


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    _columns = {
        #'active': fields.related('order_id', 'active', type='boolean', string='Active', store=False),
        'sale_line_copy_id': fields.many2one('sale.order.line', 'Orig version', required=False, readonly=False),
    }
    
    def copy_data(self, cr, uid, line_id, defaults=None, context=None):
        defaults = defaults or {}
        defaults['sale_line_copy_id'] = line_id
        return super(sale_order_line, self).copy_data(cr, uid, line_id, defaults, context)
        
    def copy(self, cr, uid, line_id, defaults, context=None):
        defaults = defaults or {}
        defaults['sale_line_copy_id'] = line_id
        return super(sale_order_line, self).copy(cr, uid, line_id, defaults, context)


class sale_order(orm.Model):
    """ Modificaciones de sale order para añadir la posibilidad de versionar el pedido de venta. """
    _inherit = "sale.order"
    
    def action_previous_version(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
            
        if not context:
            context = {}
        
        attachment_obj = self.pool['ir.attachment']
        
        orders = self.browse(cr, uid, ids, context=context)
        order_ids = []
        for order in orders:
            vals = {
                'version': (order.version and order.version or 1) + 1,
            }
            
            if not order.sale_version_id:
                vals['sale_version_id'] = order.id
            
            context['versioning'] = True
            vals['name'] = (order.sale_version_id and order.sale_version_id.name or order.name) + u" V." + ustr(vals['version'])
            new_order_id = self.copy(cr, uid, order.id, vals, context=context)
            
            attachment_ids = attachment_obj.search(cr, uid, [('res_model', '=', 'sale.order'), ('res_id', '=', order.id)])
            if attachment_ids:
                attachment_obj.write(cr, uid, attachment_ids, {'res_id': new_order_id, 'res_name': vals['name']})
            order.write({'active': False})
            order_ids.append(new_order_id)
            
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
            'res_id': order_ids and order_ids[0] or False,
        }
        
    def _get_version_ids(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for sale in self.browse(cr, uid, ids, context):
            if sale.sale_version_id:
                res[sale.id] = self.search(cr, uid, ['|', ('sale_version_id', '=', sale.sale_version_id.id), ('id', '=', sale.sale_version_id.id), ('version', '<', sale.version), '|', ('active', '=', False), ('active', '=', True)])
            else:
                res[sale.id] = []
        return res
    
    _columns = {
        'sale_version_id': fields.many2one('sale.order', 'Orig version', required=False, readonly=False),
        'version': fields.integer('Version no.', readonly=True),
        'active': fields.boolean('Active', readonly=False, help="It indicates that the sales order is active."),
        'version_ids': fields.function(_get_version_ids, method=True, type="one2many", relation='sale.order', string='Versions', readonly=True)
    }
    
    _defaults = {
        'active': True,
        'version': 0,
        'name': '/',
    }
    
    def create(self, cr, uid, vals, context=None):
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
        
        return super(sale_order, self).create(cr, uid, vals, context)


class sale_shop(orm.Model):
    _inherit = 'sale.shop'
    
    _columns = {
        'sequence_id': fields.many2one('ir.sequence', 'Entry Sequence', help="This field contains the informatin related to the numbering of the Sale Orders.", domain="[('code', '=', 'sale.order')]"),
    }
