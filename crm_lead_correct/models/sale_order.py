# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2014 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import orm, fields


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _get_connected_sale_order(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        order_id = context.get('own_sale_id')
        for sale in self.browse(cr, uid, ids, context):
            result[sale.id] = False
            if sale.id == order_id:
                result[sale.id] = True
            if self.pool['sale.order']._columns.get('sale_version_id', False):
                if sale.sale_version_id and sale.sale_version_id.id == order_id:
                    result[sale.id] = True
        return result

    _columns = {
        'connected_sale_order': fields.function(_get_connected_sale_order, string='Own Sale', type='boolean'),
        'contact_id': fields.many2one('res.partner.address.contact', 'Contact'), 
    }

    def onchange_partner_id(self, cr, uid, ids, part):
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        res['value']['contact_id'] = False
        return res

    def hook_sale_state(self, cr, uid, orders, vals, context):
        crm_obj = self.pool['crm.lead']
        state = vals.get('state')
        for order in orders:
            lead_ids = crm_obj.search(cr, uid, [('sale_order', '=', order.id)], context=context)
            if lead_ids:
                for stage in order.shop_id.crm_sale_stage_ids:
                    if stage.name == state:
                        crm_obj.write(cr, uid, lead_ids, {'stage_id': stage.stage_id.id}, context.update({'force_stage_id': True}))
        return super(sale_order, self).hook_sale_state(cr, uid, orders, vals, context)
