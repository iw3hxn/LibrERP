# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Didotech SRL (info at didotech.com)
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


class CrmSaleStage(orm.Model):
    _name = 'crm.sale.stage'
    _description = 'CRM Sale Stage'

    def _get_sale_order_state(self, cr, uid, context=None):
        state_selection = self.pool['sale.order']._columns['state'].selection
        return state_selection

    _columns = {
        'name': fields.selection(_get_sale_order_state, 'Order State', required=True),
        'shop_id': fields.many2one('sale.shop', 'Shop'),
        'stage_id': fields.many2one('crm.case.stage', 'Stage', required=True),
    }
