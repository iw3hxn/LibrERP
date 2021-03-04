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


class SaleOrder(orm.Model):
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
        res = super(SaleOrder, self).onchange_partner_id(cr, uid, ids, part)
        res['value']['contact_id'] = False
        return res

    def hook_sale_state(self, cr, uid, orders, vals, context):
        crm_model = self.pool['crm.lead']
        crm_sale_stage_model = self.pool['crm.sale.stage']
        state = vals.get('state', False)
        for order in orders:
            lead_ids = crm_model.search(cr, uid, [('sale_order_id', '=', order.id)], context=context)
            if context.get('active_model', '') == 'crm.lead':
                lead_ids.append(context.get('active_id'))
                lead_ids = list(set(lead_ids))
            if lead_ids:
                crm_sale_stage_ids = crm_sale_stage_model.search(cr, uid, [('shop_id', '=', order.shop_id.id), ('name', '=', state)], context=context)
                if crm_sale_stage_ids:
                    crm_sale_stage = crm_sale_stage_model.browse(cr, uid, crm_sale_stage_ids[0], context)
                    stage_id = crm_sale_stage.stage_id.id
                    crm_value = {'stage_id': stage_id}
                    crm_value.update(crm_model.onchange_stage_id(cr, uid, lead_ids, stage_id)['value'])
                    if crm_sale_stage.update_amount:
                        crm_value.update({
                            'planned_revenue': order.amount_untaxed
                        })
                    crm_model.write(cr, uid, lead_ids, crm_value, context.update({'force_stage_id': True}))
        return super(SaleOrder, self).hook_sale_state(cr, uid, orders, vals, context)
