# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Didotech SRL All Rights Reserved
#    d$
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


class res_partner(orm.Model):
    _inherit = 'res.partner'
    _columns = {
        'limit_note': fields.text('Limit Note'),
        'credit_limit_copy': fields.related('credit_limit', type="float", readonly=True, store=False,
                                            string='Credit Limit'),
        'validate': fields.boolean('Partner Validate'),
    }

    def onchange_credit_limit(self, cr, uid, ids, credit_limit):
        return {'value': {'credit_limit_copy': credit_limit}}

    def fields_get(self, cr, user, allfields=None, context=None, write_access=True):
        ret = super(res_partner, self).fields_get(cr, user, allfields=allfields, context=context)

        group_obj = self.pool['res.groups']
        if group_obj.user_in_group(cr, user, user, 'sale_order_confirm.credit_modifier', context=context):
            if 'credit_limit_copy' in ret:
                ret['credit_limit_copy']['invisible'] = True
            if 'limit_note' in ret:
                ret['limit_note']['readonly'] = False
        else:
            if 'credit_limit' in ret:
                ret['credit_limit']['invisible'] = True
            if 'limit_note' in ret:
                ret['limit_note']['readonly'] = True

        return ret

    def create(self, cr, uid, vals, context={}):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if vals.get('company_id', False):
            company_id = vals['company_id']
        else:
            company_id = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id.id
        company = self.pool['res.company'].browse(cr, uid, company_id, context)
        if not vals.get('credit_limit', False):
            vals['credit_limit'] = company.default_credit_limit
        if not vals.get('property_payment_term', False):
            vals['property_payment_term'] = company.default_property_payment_term and company.default_property_payment_term.id
        if not vals.get('property_account_position', False):
            vals['property_account_position'] = company.default_property_account_position and company.default_property_account_position.id
        return super(res_partner, self).create(cr, uid, vals, context=context)
