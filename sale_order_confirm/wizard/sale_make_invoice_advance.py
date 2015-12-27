# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-2015 Didotech srl (<http://www.didotech.com>)
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


class sale_advance_payment_inv(orm.TransientModel):

    _inherit = "sale.advance.payment.inv"

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        res = super(sale_advance_payment_inv, self).default_get(cr, uid, fields, context=context)
        if not res.get('product_id', False):
            product_id = self.pool['res.users'].browse(cr, uid, uid, context).company_id.default_property_advance_product_id.id
            res.update({'product_id': product_id})
        return res

    def _create_invoices(self, cr, uid, inv_values, sale_id, context):
        res = super(sale_advance_payment_inv, self)._create_invoices(cr, uid, inv_values, sale_id, context)
        self.pool['account.invoice'].write(cr, uid, res, {'advance_order_id': context['active_ids'][0]})
        return res
